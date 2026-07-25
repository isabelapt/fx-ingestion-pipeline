from datetime import date
import boto3
import pytest
from moto import mock_aws
from src.domain.entities import FXRateEntity
from src.infra.s3_repository import S3Repository


@pytest.fixture
def s3_setup():
    """Fixture to mock S3 environment using moto."""
    with mock_aws():
        bucket_name = "test-fx-bucket"
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket=bucket_name)
        yield bucket_name


def test_save_raw_rate_success(s3_setup):
    bucket_name = s3_setup
    repo = S3Repository(bucket_name=bucket_name)

    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"BRL": 5.45, "EUR": 0.92},
    )

    s3_key = repo.save_raw_rate(entity)

    assert s3_key == "raw/year=2026/month=07/day=24/USD_20260724.json"

    # Confirma que o arquivo realmente foi parar dentro do bucket S3 mockado
    s3_client = boto3.client("s3", region_name="us-east-1")
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    data = response["Body"].read().decode("utf-8")

    assert "BRL" in data
    assert "USD" in data


def test_client_error_raises_runtime_error():
    with mock_aws():
        # Força um erro de permissão (Bucket não existe)
        repo = S3Repository(bucket_name="non-existent-bucket")
        
        entity = FXRateEntity(
            base_currency="USD",
            observation_date=date(2026, 7, 24),
            rates={"BRL": 5.45},
        )
        
        with pytest.raises(RuntimeError) as excinfo:
            repo.save_raw_rate(entity)
            
        assert "Failed to persist entity to S3" in str(excinfo.value)