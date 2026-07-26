import os
from typing import Any, Dict
from src.adapters.api_client import FXApiClient
from src.infra.s3_repository import S3Repository
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entrypoint triggered by EventBridge or manual invocation."""
    base_currency = event.get("base_currency", "USD")
    observation_date = event.get("date")
    bucket_name = os.getenv("S3_BUCKET_NAME", "fx-ingestion-raw-data-dev")

    # Injeção de Dependências
    api_client = FXApiClient()
    s3_repo = S3Repository(bucket_name=bucket_name)
    use_case = IngestFXRatesUseCase(api_client=api_client, s3_repository=s3_repo)

    # Executa a pipeline
    result = use_case.execute(base_currency=base_currency, observation_date=observation_date)

    return {
        "statusCode": 200,
        "body": {
            "message": "FX Rate ingestion completed successfully",
            "identity": result.entity.identity,
            "s3_path": result.s3_path,
            "is_anomaly": result.is_anomaly,
            "quarantined": result.quarantined,
        },
    }