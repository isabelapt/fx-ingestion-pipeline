from dataclasses import dataclass
from typing import Optional
from src.adapters.api_client import FXApiClient
from src.domain.entities import FXRateEntity
from src.domain.rules import BusinessRules


@dataclass
class IngestionResult:
    """DTO representing the output of the ingestion process."""

    entity: FXRateEntity
    is_anomaly: bool


class IngestFXRatesUseCase:
    """
    Application Service / Use Case orchestrating the ingestion flow:
    1. Fetches raw rate data via API Adapter.
    2. Constructs domain entity.
    3. Evaluates business rules (e.g., market anomaly detection against historical rate).
    """

    def __init__(self, api_client: Optional[FXApiClient] = None):
        self.api_client = api_client or FXApiClient()

    def execute(
        self,
        base_currency: str = "USD",
        previous_rate: Optional[float] = None,
        target_currency: str = "BRL",
    ) -> IngestionResult:
        """
        Executes the ingestion pipeline for a given base currency.
        """
        # 1. Ingestão e validação do Schema de dados de entrada via Adapter
        schema_data = self.api_client.fetch_latest_rates(base_currency=base_currency)

        # 2. Transforma Schema em Entidade de Domínio
        entity = FXRateEntity(
            base_currency=schema_data.base_currency,
            observation_date=schema_data.observation_date,
            rates=schema_data.rates,
        )

        # 3. Aplicação de Regra de Negócio (Detecção de Anomalia)
        is_anomaly = False
        if previous_rate and target_currency in entity.rates:
            current_rate = entity.rates[target_currency]
            is_anomaly = BusinessRules.is_anomaly_rate(
                previous_rate=previous_rate, current_rate=current_rate
            )

        return IngestionResult(entity=entity, is_anomaly=is_anomaly)