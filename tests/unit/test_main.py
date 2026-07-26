from unittest.mock import MagicMock, patch
from main import run_pipeline
from src.domain.entities import FXRateEntity
from src.use_cases.ingest_fx_rates import IngestionResult


@patch("main.S3Repository")
@patch("main.IngestFXRatesUseCase")
def test_run_pipeline_success(mock_use_case_cls, mock_s3_repo_cls):
    # Setup Mocks
    mock_use_case_inst = MagicMock()
    mock_use_case_cls.return_value = mock_use_case_inst

    mock_entity = MagicMock(spec=FXRateEntity)
    mock_entity.identity = "USD_20260725"
    mock_entity.rates = {"BRL": 5.45}

    mock_use_case_inst.execute.return_value = IngestionResult(
        entity=mock_entity,
        s3_path="raw/year=2026/month=07/day=25/USD_20260725.json",
        is_anomaly=False
    )

    mock_s3_repo_inst = MagicMock()
    mock_s3_repo_cls.return_value = mock_s3_repo_inst
    mock_s3_repo_inst.save_raw_rate.return_value = "raw/year=2026/month=07/day=25/USD_20260725.json"

    # Execution
    run_pipeline(base_currency="USD", bucket_name="my-fx-bucket")

    # Assertions
    mock_use_case_inst.execute.assert_called_once_with(base_currency="USD", observation_date=None)
    mock_s3_repo_cls.assert_called_once_with(bucket_name="my-fx-bucket")