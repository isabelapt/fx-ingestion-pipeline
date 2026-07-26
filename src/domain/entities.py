from dataclasses import dataclass
from datetime import date
from typing import Dict
from src.domain.rules import BusinessRules


@dataclass(frozen=True)
class FXRateEntity:
    """
    Domain Entity representing a validated FX Rate observation.
    Maintains domain identity and encapsulates business capabilities.
    """

    base_currency: str
    observation_date: date
    rates: Dict[str, float]

    @property
    def identity(self) -> str:
        """Unique domain identity string (e.g., USD_20260724)."""
        return f"{self.base_currency.upper()}_{self.observation_date.strftime('%Y%m%d')}"

    def calculate_rate_with_spread(self, target_currency: str, spread_pct: float) -> float:
        """
        Calculates the commercial exchange rate including spread percentage.
        """
        target_upper = target_currency.strip().upper()

        if not BusinessRules.is_valid_currency_pair(self.base_currency, target_upper):
            raise ValueError("Base and target currencies cannot be identical.")

        if target_upper not in self.rates:
            raise KeyError(f"Target currency '{target_upper}' is not available in quote rates.")

        raw_rate = self.rates[target_upper]
        return round(raw_rate * (1.0 + (spread_pct / 100.0)), 6)


@dataclass(frozen=True)
class IngestionResult:
    """
    Data Transfer Object (DTO) representing the execution result of the ingestion pipeline.
    Connects domain entity with pipeline execution metadata (S3 storage and quality alerts).
    """

    entity: FXRateEntity
    s3_path: str
    is_anomaly: bool = False
    quarantined: bool = False