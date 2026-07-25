from datetime import date
import pytest
from pydantic import ValidationError
from src.domain.schemas import FXRateData


def test_valid_fx_rate_schema():
    payload = {
        "base_currency": "USD",
        "observation_date": date(2026, 7, 24),
        "rates": {"BRL": 5.45, "EUR": 0.92}
    }
    model = FXRateData(**payload)
    assert model.base_currency == "USD"
    assert model.rates["BRL"] == 5.45


def test_invalid_negative_rate_raises_validation_error():
    payload = {
        "base_currency": "USD",
        "observation_date": date(2026, 7, 24),
        "rates": {"BRL": -1.25}
    }
    with pytest.raises(ValidationError) as exc_info:
        FXRateData(**payload)
    
    assert "Exchange rates must be strictly positive" in str(exc_info.value)


def test_invalid_quote_currency_code_raises_error():
    payload = {
        "base_currency": "USD",
        "observation_date": date(2026, 7, 24),
        "rates": {"BRLX": 5.45}  # Inválido
    }
    with pytest.raises(ValidationError) as exc_info:
        FXRateData(**payload)
    assert "Invalid quote currency code 'BRLX'" in str(exc_info.value)