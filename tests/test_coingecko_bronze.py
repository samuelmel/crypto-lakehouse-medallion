"""Tests for idempotent CoinGecko Bronze ingestion."""

from datetime import date, datetime, timezone
from io import BytesIO
import json
import unittest

from src.ingestion.coingecko_bronze import (
    BronzeConfig,
    build_object_key,
    ingest_market_data,
)


class FakeResponse:
    """Minimal response double for the CoinGecko client."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeHttpClient:
    """Minimal HTTP client double."""

    def get(self, url: str, *, params: dict, timeout: int) -> FakeResponse:
        return FakeResponse(
            {
                "bitcoin": {
                    "usd": 60000,
                    "usd_market_cap": 1000000,
                }
            }
        )


class FakeS3Client:
    """In-memory object store used to test overwrite behavior."""

    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}
        self.put_calls = 0

    def put_object(self, *, Bucket: str, Key: str, Body: BytesIO, ContentType: str) -> None:
        self.put_calls += 1
        self.objects[(Bucket, Key)] = Body.read()


class BronzeIngestionTests(unittest.TestCase):
    """Behavior tests for the Bronze writer."""

    def setUp(self) -> None:
        self.config = BronzeConfig(
            api_base_url="https://api.example.test",
            minio_endpoint="http://minio:9000",
            minio_region="us-east-1",
            minio_access_key="access-key",
            minio_secret_key="secret-key",
            bronze_bucket="bronze",
            crypto_ids=("bitcoin", "ethereum"),
        )

    def test_repeated_run_overwrites_same_logical_object(self) -> None:
        storage = FakeS3Client()
        run_date = date(2026, 9, 8)
        first_time = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
        second_time = datetime(2026, 9, 8, 11, tzinfo=timezone.utc)

        first_key = ingest_market_data(
            self.config,
            s3_client=storage,
            http_client=FakeHttpClient(),
            reference_date=run_date,
            ingested_at=first_time,
        )
        second_key = ingest_market_data(
            self.config,
            s3_client=storage,
            http_client=FakeHttpClient(),
            reference_date=run_date,
            ingested_at=second_time,
        )

        self.assertEqual(first_key, second_key)
        self.assertEqual(storage.put_calls, 2)
        self.assertEqual(len(storage.objects), 1)
        payload = json.loads(next(iter(storage.objects.values())))
        self.assertEqual(payload["reference_date"], "2026-09-08")
        self.assertEqual(payload["ingested_at"], second_time.isoformat())

    def test_object_key_is_deterministic(self) -> None:
        expected = "market/date=2026-09-08/assets=af6df774bb89.json"
        self.assertEqual(
            build_object_key(date(2026, 9, 8), ("ethereum", "bitcoin")),
            expected,
        )


if __name__ == "__main__":
    unittest.main()
