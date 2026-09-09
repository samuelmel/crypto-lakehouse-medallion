"""Upload Gold Parquet objects from MinIO to Databricks Volumes."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import quote


class ObjectBody(Protocol):
    """Readable object body returned by an S3 client."""

    def read(self, amount: int = -1) -> bytes:
        """Read bytes from the object."""


class S3Client(Protocol):
    """Minimal S3 client contract used by the uploader."""

    def list_objects_v2(self, **kwargs: Any) -> dict[str, Any]:
        """List objects in a bucket."""

    def get_object(self, **kwargs: Any) -> dict[str, Any]:
        """Read one object from a bucket."""


class HttpClient(Protocol):
    """Minimal HTTP client contract used by the uploader."""

    def put(self, url: str, **kwargs: Any) -> Any:
        """Upload bytes to an HTTP endpoint."""


@dataclass(frozen=True)
class DatabricksUploadConfig:
    """Configuration for a Gold-to-Volume upload."""

    databricks_host: str
    databricks_token: str
    volume_path: str
    minio_endpoint: str
    minio_region: str
    minio_access_key: str
    minio_secret_key: str
    gold_bucket: str = "gold"
    gold_prefix: str = ""
    request_timeout_seconds: int = 60

    @classmethod
    def from_environment(cls) -> "DatabricksUploadConfig":
        """Build configuration from environment variables."""
        return cls(
            databricks_host=os.environ["DATABRICKS_HOST"].rstrip("/"),
            databricks_token=os.environ["DATABRICKS_TOKEN"],
            volume_path=os.environ["DATABRICKS_VOLUME_PATH"].rstrip("/"),
            minio_endpoint=os.environ["MINIO_ENDPOINT"],
            minio_region=os.getenv("MINIO_REGION", "us-east-1"),
            minio_access_key=os.environ["MINIO_ROOT_USER"],
            minio_secret_key=os.environ["MINIO_ROOT_PASSWORD"],
            gold_bucket=os.getenv("MINIO_BUCKET_GOLD", "gold"),
            gold_prefix=os.getenv("DATABRICKS_GOLD_PREFIX", ""),
            request_timeout_seconds=int(
                os.getenv("DATABRICKS_REQUEST_TIMEOUT_SECONDS", "60")
            ),
        )


def create_s3_client(config: DatabricksUploadConfig) -> S3Client:
    """Create an S3 client configured for the local MinIO endpoint."""
    import boto3
    from botocore.client import BaseClient
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=config.minio_endpoint,
        aws_access_key_id=config.minio_access_key,
        aws_secret_access_key=config.minio_secret_key,
        region_name=config.minio_region,
        config=Config(signature_version="s3v4"),
    )


def list_gold_objects(
    s3_client: S3Client,
    bucket: str,
    prefix: str = "",
) -> list[str]:
    """Return Parquet object keys from the Gold bucket."""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return sorted(
        item["Key"]
        for item in response.get("Contents", [])
        if item["Key"].lower().endswith(".parquet")
    )


def upload_gold_files(
    config: DatabricksUploadConfig,
    *,
    s3_client: S3Client | None = None,
    http_client: HttpClient | None = None,
) -> list[str]:
    """Upload every Gold Parquet to the configured Databricks Volume.

    The Databricks Files API replaces an existing file at the same path, making
    repeated runs idempotent for each Gold object.
    """
    if http_client is None:
        import requests

        http_client = requests

    storage_client = s3_client or create_s3_client(config)
    object_keys = list_gold_objects(
        storage_client,
        config.gold_bucket,
        config.gold_prefix,
    )
    uploaded_paths: list[str] = []
    headers = {
        "Authorization": f"Bearer {config.databricks_token}",
        "Content-Type": "application/octet-stream",
    }

    for object_key in object_keys:
        relative_key = object_key.removeprefix(config.gold_prefix).lstrip("/")
        destination_path = f"{config.volume_path}/{relative_key}"
        encoded_path = quote(destination_path, safe="/")
        response = storage_client.get_object(
            Bucket=config.gold_bucket,
            Key=object_key,
        )
        upload_response = http_client.put(
            f"{config.databricks_host}/api/2.0/fs/files/{encoded_path}",
            headers=headers,
            data=response["Body"],
            timeout=config.request_timeout_seconds,
        )
        upload_response.raise_for_status()
        uploaded_paths.append(destination_path)

    return uploaded_paths
