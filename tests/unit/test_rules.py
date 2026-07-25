from src.domain.rules import BusinessRules


def test_valid_currency_pair_rule():
    assert BusinessRules.is_valid_currency_pair("USD", "BRL") is True
    assert BusinessRules.is_valid_currency_pair("USD", "usd") is False


def test_anomaly_rate_detection():
    # 10% variation -> Normal
    assert BusinessRules.is_anomaly_rate(previous_rate=5.0, current_rate=5.5) is False

    # 20% variation -> Anomaly (> 15%)
    assert BusinessRules.is_anomaly_rate(previous_rate=5.0, current_rate=6.0) is True

    # Taxas zeradas ou negativas -> Deve retornar False
    assert BusinessRules.is_anomaly_rate(previous_rate=0.0, current_rate=5.5) is False
    assert BusinessRules.is_anomaly_rate(previous_rate=5.0, current_rate=0.0) is False
    assert BusinessRules.is_anomaly_rate(previous_rate=-1.0, current_rate=5.5) is False
    assert BusinessRules.is_anomaly_rate(previous_rate=5.0, current_rate=-1.0) is False