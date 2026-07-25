from datetime import date
from unittest.mock import MagicMock
from src.domain.schemas import FXRateData
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase


def test_ingest_fx_rates_use_case_success():
    # Mock do ApiClient
    mock_api_client = MagicMock()
    mock_api_client.fetch_latest_rates.return_value = FXRateData(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"BRL": 5.00, "EUR": 0.90},
    )

    use_case = IngestFXRatesUseCase(api_client=mock_api_client)
    result = use_case.execute(base_currency="USD", previous_rate=4.90, target_currency="BRL")

    assert result.entity.identity == "USD_20260724"
    assert result.entity.rates["BRL"] == 5.00
    assert result.is_anomaly is False
    mock_api_client.fetch_latest_rates.assert_called_once_with(base_currency="USD")


def test_ingest_fx_rates_use_case_detects_anomaly():
    mock_api_client = MagicMock()
    mock_api_client.fetch_latest_rates.return_value = FXRateData(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"BRL": 6.50},  # Variação de 30% em relação a 5.00 (> 15%)
    )

    use_case = IngestFXRatesUseCase(api_client=mock_api_client)
    result = use_case.execute(base_currency="USD", previous_rate=5.00, target_currency="BRL")

    assert result.is_anomaly is True