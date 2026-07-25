from datetime import date
import pytest
from unittest.mock import patch, MagicMock
import httpx
from src.adapters.api_client import FXApiClient


def test_fetch_latest_rates_success():
    """Validates that FXApiClient correctly fetches and adapts API response to FXRateData."""
    mock_payload = {
        "amount": 1.0,
        "base": "USD",
        "date": "2026-07-24",
        "rates": {"BRL": 5.45, "EUR": 0.92},
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    # raise_for_status não faz nada por padrão (sucesso)

    with patch("httpx.get", return_value=mock_response) as mock_get:
        client = FXApiClient()
        result = client.fetch_latest_rates("USD")

        mock_get.assert_called_once_with("https://api.frankfurter.dev/v1/latest", params={"base": "USD"}, timeout=10.0)

        assert result.base_currency == "USD"
        assert result.rates["BRL"] == 5.45
        assert result.observation_date == date(2026, 7, 24)


def test_fetch_latest_rates_http_error_raises_exception():
    """Validates that HTTP errors (e.g., 500 Internal Server Error) are caught and wrapped."""
    mock_response = MagicMock()
    # Simula que o raise_for_status lança um erro HTTP do httpx
    mock_response.raise_for_status.side_effect = httpx.HTTPError("Mocked HTTP Error")

    with patch("httpx.get", return_value=mock_response):
        client = FXApiClient()

        with pytest.raises(RuntimeError) as exc_info:
            client.fetch_latest_rates("USD")

        assert "Failed to fetch rates from external API" in str(exc_info.value)
        
@patch("httpx.get")
def test_fetch_rates_historical_success(mock_get):
    mock_response = {
        "amount": 1.0,
        "base": "USD",
        "date": "1999-01-04",
        "rates": {"EUR": 0.84825},
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    client = FXApiClient()
    historical_date = date(1999, 1, 4)
    result = client.fetch_rates(base_currency="USD", observation_date=historical_date)

    assert result.observation_date == date(1999, 1, 4)
    assert result.rates["EUR"] == 0.84825

    mock_get.assert_called_once_with(
        "https://api.frankfurter.dev/v1/1999-01-04",
        params={"base": "USD"},
        timeout=10.0,
    )
