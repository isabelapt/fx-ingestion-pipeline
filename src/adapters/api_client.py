from datetime import date
from typing import Optional
import httpx
# pyrefly: ignore [missing-import]
from src.domain.schemas import FXRateData


class FXApiClient:
    """
    Adapter responsible for fetching daily foreign exchange rates from an external API (Frankfurter).
    Converts raw JSON responses into the Domain's FXRateData Contract.
    """

    def __init__(self, base_url: str = "https://api.frankfurter.dev/v1", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_rates(
        self, base_currency: str = "USD", observation_date: Optional[date] = None
    ) -> FXRateData:
        """
        Fetches FX rates. If observation_date is provided, fetches historical data;
        otherwise, fetches the latest rates.
        """
        endpoint = observation_date.isoformat() if observation_date else "latest"
        url = f"{self.base_url}/{endpoint}"
        params = {"base": base_currency.upper()}

        try:
            response = httpx.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()

            return FXRateData(
                base_currency=payload["base"],
                observation_date=date.fromisoformat(payload["date"]),
                rates=payload["rates"],
            )
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch rates from external API: {str(e)}") from e

    def fetch_latest_rates(self, base_currency: str = "USD") -> FXRateData:
        return self.fetch_rates(base_currency=base_currency)