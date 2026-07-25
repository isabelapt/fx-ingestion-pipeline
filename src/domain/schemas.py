from datetime import date
from typing import Dict
from pydantic import BaseModel, Field, field_validator


class FXRateData(BaseModel):
    """
    Data Contract for incoming Foreign Exchange rates from external SOR/APIs.
    Enforces strict typing, currency codes, and non-negative rate bounds.
    """
    base_currency: str = Field(
        ..., 
        min_length=3, 
        max_length=3, 
        description="ISO 4217 3-letter currency code (e.g., USD, EUR)"
    )
    observation_date: date = Field(
        ..., 
        description="Date of the exchange rate observation"
    )
    rates: Dict[str, float] = Field(
        ..., 
        description="Map of quote currency code to exchange rate"
    )

    @field_validator("rates")
    def validate_positive_rates(cls, rates: Dict[str, float]) -> Dict[str, float]:
        for currency, rate in rates.items():
            if rate <= 0:
                raise ValueError(f"Invalid rate for {currency}: {rate}. Exchange rates must be strictly positive.")
            if len(currency) != 3:
                raise ValueError(f"Invalid quote currency code '{currency}'. Must be 3 characters.")
        return rates