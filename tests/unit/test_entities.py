from datetime import date
import pytest
from src.domain.entities import FXRateEntity


def test_fx_rate_entity_identity():
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"BRL": 5.45, "EUR": 0.92},
    )
    assert entity.identity == "USD_20260724"


def test_fx_rate_entity_spread_calculation():
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"BRL": 5.00},
    )
    # 5.00 + 2% spread = 5.10
    result = entity.calculate_rate_with_spread("BRL", spread_pct=2.0)
    assert result == 5.10


def test_fx_rate_entity_invalid_pair_spread_raises_error():
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"USD": 1.00},
    )
    with pytest.raises(ValueError, match="Base and target currencies cannot be identical"):
        entity.calculate_rate_with_spread("USD", spread_pct=1.0)


def test_fx_rate_invalid_target_currenry_raises_error():
    entity = FXRateEntity(
        base_currency="USD",
        observation_date=date(2026, 7, 24),
        rates={"USD": 1.00},
    )
    with pytest.raises(KeyError, match="Target currency 'EUR' is not available in quote rates."):
        entity.calculate_rate_with_spread("EUR", spread_pct=1.0)