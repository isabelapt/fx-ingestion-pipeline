import argparse
from datetime import date
import sys
from src.adapters.api_client import FXApiClient
from src.infra.s3_repository import S3Repository
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase


def run_pipeline(
    base_currency: str,
     bucket_name: str | None = None,
     observation_date: date | None = None) -> None:
    """
    Execute the end-to-end FX rate ingestion pipeline.
    
    Parameters:
        base_currency (str): Currency used as the basis for the exchange rates.
        bucket_name (str | None): Target S3 bucket name, or None to use the default CLI bucket.
        observation_date (date | None): Historical date for the rates, or None for the current date.
    """
    print(f"🚀 Starting FX Rate Ingestion Pipeline for Base Currency: [{base_currency}]")

    # 1. Instancia dependências e injeta no Use Case
    api_client = FXApiClient()
    repo = S3Repository(bucket_name=bucket_name or "dummy-bucket-for-cli-non-s3-runs")
    use_case = IngestFXRatesUseCase(api_client=api_client, s3_repository=repo)

    # 2. Executa a Ingestão, Regras do Domínio e Persistência S3
    result = use_case.execute(base_currency=base_currency, observation_date=observation_date)
    print(f"✅ Ingestion successful! Identity: {result.entity.identity}")
    print(f"📊 Rates fetched for {len(result.entity.rates)} currencies.")
    print(f"✨ Successfully persisted to S3 Path: {result.s3_path}")

    if result.is_anomaly:
        print("⚠️ WARNING: Detected price anomaly based on business rules!")


def main() -> None:
    """
    Parse command-line options and run the FX rate ingestion pipeline.
    
    The command accepts a base currency, an optional S3 bucket, and an optional historical observation date. Pipeline failures are reported to standard error and terminate the process with status code 1.
    """
    parser = argparse.ArgumentParser(description="FX Ingestion Pipeline CLI")
    parser.add_argument(
        "--base",
        type=str,
        default="USD",
        help="Base currency for exchange rates (e.g., USD, EUR, BRL)",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        default=None,
        help="AWS S3 bucket name to persist raw JSON data",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Optional historical date to fetch in YYYY-MM-DD format (defaults to latest)",
    )

    args = parser.parse_args()

    try:
        parsed_date = date.fromisoformat(args.date) if args.date else None

        run_pipeline(
            base_currency=args.base.upper(),
             bucket_name=args.bucket,
             observation_date=parsed_date
             )
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()