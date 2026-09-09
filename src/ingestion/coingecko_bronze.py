"""Ingest CoinGecko market data into the MinIO Bronze layer."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from io import BytesIO
from typing import TYPE_CHECKING, Any, Protocol, Sequence

if TYPE_CHECKING:
    from botocore.client import BaseClient


class HttpClient(Protocol):
    """Minimal HTTP client contract used by the ingestion service."""

    def get(self, url: str, *, params: dict[str, str], timeout: int) -> Any:
        """Request a resource from the API."""


@dataclass(frozen=True)
class BronzeConfig:
    """Runtime configuration for a Bronze ingestion run."""

    api_base_url: str
    minio_endpoint: str
    minio_region: str
    minio_access_key: str
    minio_secret_key: str
    bronze_bucket: str
    crypto_ids: tuple[str, ...]
    vs_currency: str = "usd"
    request_timeout_seconds: int = 30

    @classmethod
    def from_environment(cls) -> "BronzeConfig":
        """Build configuration from environment variables."""
        crypto_ids = tuple(
            item.strip()
            for item in os.getenv("COINGECKO_CRYPTO_IDS", "bitcoin,ethereum").split(",")
            if item.strip()
        )
        return cls(
            api_base_url=os.environ["COINGECKO_BASE_URL"].rstrip("/"),
            minio_endpoint=os.environ["MINIO_ENDPOINT"],
            minio_region=os.getenv("MINIO_REGION", "us-east-1"),
            minio_access_key=os.environ["MINIO_ROOT_USER"],
            minio_secret_key=os.environ["MINIO_ROOT_PASSWORD"],
            bronze_bucket=os.getenv("MINIO_BUCKET_BRONZE", "bronze"),
            crypto_ids=crypto_ids,
            vs_currency=os.getenv("COINGECKO_VS_CURRENCY", "usd"),
            request_timeout_seconds=int(
                os.getenv("COINGECKO_REQUEST_TIMEOUT_SECONDS", "30")
            ),
        )


class CoinGeckoClient:
    """Client for the CoinGecko simple price endpoint."""

    def __init__(
        self,
        base_url: str,
        http_client: HttpClient | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        if http_client is None:
            import requests

            http_client = requests
        self.http_client = http_client
        self.timeout_seconds = timeout_seconds

    def get_market_data(
        self,
        crypto_ids: Sequence[str],
        vs_currency: str = "usd",
    ) -> dict[str, Any]:
        """Fetch current prices and market metrics for selected assets."""
        if not crypto_ids:
            raise ValueError("At least one cryptocurrency id is required")

        response = self.http_client.get(
            f"{self.base_url}/simple/price",
            params={
                "ids": ",".join(sorted(set(crypto_ids))),
                "vs_currencies": vs_currency,
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


def build_object_key(reference_date: date, crypto_ids: Sequence[str]) -> str:
    """Return a deterministic Bronze key for one daily market snapshot."""
    normalized_ids = ",".join(sorted(set(crypto_ids)))
    digest = hashlib.sha256(normalized_ids.encode("utf-8")).hexdigest()[:12]
    return f"market/date={reference_date.isoformat()}/assets={digest}.json"


def build_payload(
    market_data: dict[str, Any],
    crypto_ids: Sequence[str],
    vs_currency: str,
    reference_date: date,
    ingested_at: datetime,
) -> dict[str, Any]:
    """Wrap the untouched API response with ingestion metadata."""
    return {
        "source": "coingecko",
        "endpoint": "/simple/price",
        "reference_date": reference_date.isoformat(),
        "ingested_at": ingested_at.isoformat(),
        "crypto_ids": sorted(set(crypto_ids)),
        "vs_currency": vs_currency,
        "data": market_data,
    }


def create_s3_client(config: BronzeConfig) -> "BaseClient":
    """Create an S3 client configured for MinIO."""
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


def ingest_market_data(
    config: BronzeConfig,
    *,
    s3_client: BaseClient | Any | None = None,
    http_client: HttpClient | None = None,
    reference_date: date | None = None,
    ingested_at: datetime | None = None,
) -> str:
    """Fetch market data and overwrite its deterministic Bronze object."""
    run_date = reference_date or datetime.now(UTC).date()
    ingestion_time = ingested_at or datetime.now(UTC)
    client = CoinGeckoClient(
        config.api_base_url,
        http_client=http_client,
        timeout_seconds=config.request_timeout_seconds,
    )
    market_data = client.get_market_data(config.crypto_ids, config.vs_currency)
    payload = build_payload(
        market_data,
        config.crypto_ids,
        config.vs_currency,
        run_date,
        ingestion_time,
    )
    object_key = build_object_key(run_date, config.crypto_ids)
    storage_client = s3_client or create_s3_client(config)
    storage_client.put_object(
        Bucket=config.bronze_bucket,
        Key=object_key,
        Body=BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")),
        ContentType="application/json",
    )
    return object_key
