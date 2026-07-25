class BusinessRules:
    """
    Pure financial business rules and invariants for Foreign Exchange (FX) data processing.
    """

    MAX_DAILY_VARIATION_PCT: float = 15.0  # Threshold for market anomaly detection (15%)

    @staticmethod
    def is_valid_currency_pair(base: str, target: str) -> bool:
        """
        Rule: Base and target currencies cannot be identical (e.g., USD/USD is invalid).
        """
        return base.strip().upper() != target.strip().upper()

    @staticmethod
    def is_anomaly_rate(previous_rate: float, current_rate: float) -> bool:
        """
        Rule: Identifies whether a currency rate fluctuation exceeds the acceptable volatility threshold.
        """
        if previous_rate <= 0 or current_rate <= 0:
            return False

        variation_pct = abs((current_rate - previous_rate) / previous_rate) * 100.0
        return variation_pct > BusinessRules.MAX_DAILY_VARIATION_PCT