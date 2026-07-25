import argparse
import sys
from src.infra.s3_repository import S3Repository
from src.use_cases.ingest_fx_rates import IngestFXRatesUseCase


def run_pipeline(base_currency: str, bucket_name: str | None = None) -> None:
    """
    Executes the end-to-end FX Rate ingestion pipeline.
    """
    print(f"🚀 Starting FX Rate Ingestion Pipeline for Base Currency: [{base_currency}]")

    # 1. Instancia o Use Case
    use_case = IngestFXRatesUseCase()

    # 2. Executa a Ingestão e Regras do Domínio
    result = use_case.execute(base_currency=base_currency)
    print(f"✅ Ingestion successful! Identity: {result.entity.identity}")
    print(f"📊 Rates fetched for {len(result.entity.rates)} currencies.")

    if result.is_anomaly:
        print("⚠️ WARNING: Detected price anomaly based on business rules!")

    # 3. Persistência em S3 (Se um bucket for fornecido)
    if bucket_name:
        print(f"📦 Persisting raw data to S3 bucket: [{bucket_name}]...")
        repo = S3Repository(bucket_name=bucket_name)
        s3_key = repo.save_raw_rate(result.entity)
        print(f"✨ Successfully persisted to S3 Key: {s3_key}")
    else:
        print("ℹ️ No S3 bucket specified. Skipping persistence step.")


def main() -> None:
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

    args = parser.parse_args()

    try:
        run_pipeline(base_currency=args.base.upper(), bucket_name=args.bucket)
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()