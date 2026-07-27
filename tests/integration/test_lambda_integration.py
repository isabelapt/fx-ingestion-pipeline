import json
import os
from unittest.mock import patch
import pytest
import boto3
from moto import mock_aws
from src.adapters.lambda_handler import lambda_handler

from datetime import date
from src.domain.schemas import FXRateData

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["S3_BUCKET_NAME"] = "test-fx-bucket"

@mock_aws
@patch("src.adapters.api_client.FXApiClient.fetch_rates")
def test_lambda_handler_full_integration(mock_fetch_rates, aws_credentials):
    bucket_name = "test-fx-bucket"
    
    # 1. Instancia o S3 no Moto
    s3_client = boto3.client("s3", region_name="us-east-1")
    s3_client.create_bucket(Bucket=bucket_name)

    # 2. Mocka apenas a requisição HTTP da API externa
    mock_fetch_rates.return_value = FXRateData(
        base_currency="USD",
        observation_date=date(2026, 7, 26),
        rates={"BRL": 5.40, "EUR": 0.92}
    )

    # 3. Dispara o Handler da Lambda
    event = {"base_currency": "USD", "date": "2026-07-26"}
    response = lambda_handler(event, None)

    # 4. Valida a resposta do Handler
    assert response["statusCode"] == 200
    assert response["body"]["identity"] == "USD_20260726"

    # 5. Confirma se o payload realmente foi gravado no S3
    expected_key = "raw/year=2026/month=07/day=26/USD_20260726.json"
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=expected_key)
    file_data = json.loads(s3_object["Body"].read().decode("utf-8"))
    assert file_data["base_currency"] == "USD"
    assert file_data["rates"]["BRL"] == 5.40