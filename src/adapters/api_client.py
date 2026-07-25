from datetime import date
import httpx
from src.domain.schemas import FXRateData


class FXApiClient:
    """
    Adapter responsible for fetching daily foreign exchange rates from an external API (Frankfurter).
    Converts raw JSON responses into the Domain's FXRateData Contract.
    """

    def __init__(self, base_url: str = "https://api.frankfurter.dev/v1"):
        self.base_url = base_url

    def fetch_latest_rates(self, base_currency: str = "USD") -> FXRateData:
        """
        Fetches latest rates for a given base currency and validates the payload against the domain schema.
        """
        url = f"{self.base_url}/latest?base={base_currency}"

        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
            payload = response.json()

            # Adapta e valida a resposta bruta no Schema do Domínio
            return FXRateData(
                base_currency=payload["base"],
                observation_date=date.fromisoformat(payload["date"]),
                rates=payload["rates"],
            )
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch rates from external API: {str(e)}") from e