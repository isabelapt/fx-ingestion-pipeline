from datetime import date
from unittest.mock import MagicMock
from src.domain.entities import IngestionResult, FXRateEntity
from src.domain.schemas import FXRateData
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase

def test_ingest_fx_rates_use_case_success():
    # Mocks
    mock_api = MagicMock()
    mock_s3 = MagicMock()

    mock_api.fetch_rates.side_effect = [
        FXRateData(
            base_currency="USD",
            observation_date=date(2026, 7, 26),
            rates={"BRL": 5.40, "EUR": 0.92},
        ),
        FXRateData(
            base_currency="USD",
            observation_date=date(2026, 7, 25),
            rates={"BRL": 5.35, "EUR": 0.91},
        )
    ]
    mock_s3.save_raw_rate.return_value = "raw/year=2026/month=07/day=26/USD_20260726.json"

    # Instantiate Use Case
    use_case = IngestFXRatesUseCase(api_client=mock_api, s3_repository=mock_s3)
    result = use_case.execute(base_currency="USD", observation_date="2026-07-26")

    # Assertions
    assert isinstance(result, IngestionResult)
    assert isinstance(result.entity, FXRateEntity)
    assert result.entity.base_currency == "USD"
    assert result.entity.identity == "USD_20260726"
    assert result.s3_path == "raw/year=2026/month=07/day=26/USD_20260726.json"
    assert result.is_anomaly is False

    assert mock_api.fetch_rates.call_count == 2
    mock_s3.save_raw_rate.assert_called_once()

def test_ingest_fx_rates_use_case_anomaly():
    mock_api = MagicMock()
    mock_s3 = MagicMock()

    # Yesterday's rates are significantly different to trigger an anomaly
    mock_api.fetch_rates.side_effect = [
        FXRateData(
            base_currency="USD",
            observation_date=date(2026, 7, 26),
            rates={"BRL": 5.40},
        ),
        FXRateData(
            base_currency="USD",
            observation_date=date(2026, 7, 25),
            rates={"BRL": 4.50}, # > 10% change triggers anomaly
        )
    ]
    mock_s3.save_raw_rate.return_value = "raw/year=2026/month=07/day=26/USD_20260726.json"

    use_case = IngestFXRatesUseCase(api_client=mock_api, s3_repository=mock_s3)
    result = use_case.execute(base_currency="USD", observation_date="2026-07-26")

    assert result.is_anomaly is True
    assert result.quarantined is True

def test_ingest_fx_rates_use_case_history_error():
    mock_api = MagicMock()
    mock_s3 = MagicMock()

    # First call succeeds, second call throws exception
    mock_api.fetch_rates.side_effect = [
        FXRateData(
            base_currency="USD",
            observation_date=date(2026, 7, 26),
            rates={"BRL": 5.40},
        ),
        Exception("API Down")
    ]
    mock_s3.save_raw_rate.return_value = "raw/year=2026/month=07/day=26/USD_20260726.json"

    use_case = IngestFXRatesUseCase(api_client=mock_api, s3_repository=mock_s3)
    result = use_case.execute(base_currency="USD", observation_date="2026-07-26")

    # Ingestion succeeds, proceeds without anomaly detection
    assert result.is_anomaly is False
    assert result.quarantined is False
    assert mock_api.fetch_rates.call_count == 2