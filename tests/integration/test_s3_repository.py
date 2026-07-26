import json
import os
import pytest
import boto3
from moto import mock_aws
from src.infra.s3_repository import S3Repository

@pytest.fixture
def aws_credentials():
    """
    Configure environment variables with test AWS credentials and region settings for moto-backed tests.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@mock_aws
def test_s3_repository_save_raw_rate_integration(aws_credentials):
    bucket_name = "test-fx-ingestion-bucket"
    
    # Prepara o bucket S3 em memória
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket=bucket_name)

    # Executa o repositório real
    repo = S3Repository(bucket_name=bucket_name)
    from datetime import date
    from src.domain.entities import FXRateEntity
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 26),
        rates={"BRL": 5.25}
    )
    
    s3_path = repo.save_raw_rate(entity)

    # Valida caminho da partição
    assert "raw/year=2026/month=07/day=26/USD_20260726.json" in s3_path

    # Lê o objeto gravado no S3 virtualizado para validar conteúdo
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_path)
    saved_content = json.loads(response["Body"].read().decode("utf-8"))
    
    assert saved_content["base_currency"] == "USD"
    assert saved_content["rates"]["BRL"] == 5.25

@mock_aws
def test_client_error_raises_runtime_error(aws_credentials):
    # Non-existent bucket forces a ClientError from boto3
    repo = S3Repository(bucket_name="non-existent-bucket-name")
    from datetime import date
    from src.domain.entities import FXRateEntity
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 26),
        rates={"BRL": 5.25}
    )
    with pytest.raises(RuntimeError) as excinfo:
        repo.save_raw_rate(entity)
    assert "Failed to persist entity to S3" in str(excinfo.value)