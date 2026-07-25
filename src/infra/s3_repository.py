import json
import boto3
from botocore.exceptions import ClientError
from src.domain.entities import FXRateEntity


class S3Repository:
    """
    Infrastructure Repository responsible for persisting domain entities to AWS S3.
    """

    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client("s3", region_name=region_name)

    def save_raw_rate(self, entity: FXRateEntity) -> str:
        """
        Saves a raw FX rate entity as a JSON file in the S3 bucket under the raw/ partition.
        Returns the generated S3 object key.
        """
        s3_key = f"raw/year={entity.observation_date.year}/month={entity.observation_date.month:02d}/day={entity.observation_date.day:02d}/{entity.identity}.json"

        payload = {
            "base_currency": entity.base_currency,
            "observation_date": str(entity.observation_date),
            "rates": entity.rates,
        }

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(payload),
                ContentType="application/json",
            )
            return s3_key
        except ClientError as e:
            raise RuntimeError(f"Failed to persist entity to S3: {str(e)}") from e