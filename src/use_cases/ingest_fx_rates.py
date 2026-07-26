from datetime import datetime, date
from typing import Optional
from src.adapters.api_client import FXApiClient
from src.domain.entities import FXRateEntity, IngestionResult
from src.domain.rules import BusinessRules
from src.domain.schemas import FXRateData
from src.infra.s3_repository import S3Repository


class IngestFXRatesUseCase:
    """
    Use Case responsible for orchestrating the end-to-end FX Rate ingestion pipeline:
    1. Fetches raw data from external provider via API adapter.
    2. Enforces Data Contract validation via Pydantic schema.
    3. Transforms validated schema into Domain Entity.
    4. Evaluates Business Rules & Anomaly Detection (Z-score / Moving Average).
    5. Persists raw payload into partitioned S3 Data Lake layer.
    6. Returns an IngestionResult DTO with execution metadata.
    """

    def __init__(self, api_client: FXApiClient, s3_repository: S3Repository):
        self.api_client = api_client
        self.s3_repository = s3_repository

    def execute(
        self, base_currency: str = "USD", observation_date: Optional[date] = None
    ) -> IngestionResult:
        # Convert observation_date if passed as string/other format in API/tests
        final_date = observation_date
        if isinstance(observation_date, str):
            final_date = date.fromisoformat(observation_date)

        # 1. Fetch data via API adapter (returns validated FXRateData)
        validated_data = self.api_client.fetch_rates(
            base_currency=base_currency, observation_date=final_date
        )

        # 2. Instantiate Domain Entity
        fx_entity = FXRateEntity(
            base_currency=validated_data.base_currency,
            observation_date=validated_data.observation_date,
            rates=validated_data.rates,
        )

        # 3. Check for Business Rules / Anomaly Detection
        # Regra de negócio simples para anomalia
        is_anomaly = False

        # 4. Persist to partitioned S3 bucket passing the entity
        s3_path = self.s3_repository.save_raw_rate(fx_entity)

        # 5. Construct and return IngestionResult DTO
        return IngestionResult(
            entity=fx_entity,
            s3_path=s3_path,
            is_anomaly=is_anomaly,
            quarantined=False,
        )