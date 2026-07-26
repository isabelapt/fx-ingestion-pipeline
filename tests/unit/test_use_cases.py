from datetime import date
from unittest.mock import MagicMock
from src.domain.entities import IngestionResult, FXRateEntity
from src.domain.schemas import FXRateData
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase

def test_ingest_fx_rates_use_case_success():
    # Mocks
    mock_api = MagicMock()
    mock_s3 = MagicMock()

    mock_api.fetch_rates.return_value = FXRateData(
        base_currency="USD",
        observation_date=date(2026, 7, 26),
        rates={"BRL": 5.40, "EUR": 0.92},
    )
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

    mock_api.fetch_rates.assert_called_once_with(base_currency="USD", observation_date=date(2026, 7, 26))
    mock_s3.save_raw_rate.assert_called_once()