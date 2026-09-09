"""Tests for the MinIO-to-Databricks Gold uploader."""

from io import BytesIO
import unittest

from src.databricks.upload_gold import (
    DatabricksUploadConfig,
    list_gold_objects,
    upload_gold_files,
)


class FakeUploadResponse:
    """Successful HTTP response double."""

    def raise_for_status(self) -> None:
        return None


class FakeS3Client:
    """In-memory S3 double."""

    def __init__(self) -> None:
        self.objects = {
            "dim_cryptos/dim_cryptos.parquet": b"dim",
            "fact_precos_mercado/fact_precos_mercado.parquet": b"fact",
            "README.txt": b"ignore",
        }

    def list_objects_v2(self, **kwargs: object) -> dict:
        return {"Contents": [{"Key": key} for key in self.objects]}

    def get_object(self, **kwargs: object) -> dict:
        return {"Body": BytesIO(self.objects[kwargs["Key"]])}


class FakeHttpClient:
    """HTTP client double that records uploads."""

    def __init__(self) -> None:
        self.uploads: list[dict] = []

    def put(self, url: str, **kwargs: object) -> FakeUploadResponse:
        body = kwargs["data"]
        self.uploads.append(
            {
                "url": url,
                "body": body.read(),
                "headers": kwargs["headers"],
            }
        )
        return FakeUploadResponse()


class DatabricksUploadTests(unittest.TestCase):
    """Behavior tests for Gold uploads."""

    def setUp(self) -> None:
        self.config = DatabricksUploadConfig(
            databricks_host="https://workspace.cloud.databricks.com",
            databricks_token="test-token",
            volume_path="/Volumes/main/gold/crypto",
            minio_endpoint="http://minio:9000",
            minio_region="us-east-1",
            minio_access_key="access",
            minio_secret_key="secret",
        )

    def test_lists_only_parquet_objects(self) -> None:
        keys = list_gold_objects(FakeS3Client(), "gold")
        self.assertEqual(
            keys,
            [
                "dim_cryptos/dim_cryptos.parquet",
                "fact_precos_mercado/fact_precos_mercado.parquet",
            ],
        )

    def test_uploads_gold_objects_to_volume_paths(self) -> None:
        http_client = FakeHttpClient()
        uploaded = upload_gold_files(
            self.config,
            s3_client=FakeS3Client(),
            http_client=http_client,
        )

        self.assertEqual(
            uploaded,
            [
                "/Volumes/main/gold/crypto/dim_cryptos/dim_cryptos.parquet",
                "/Volumes/main/gold/crypto/fact_precos_mercado/fact_precos_mercado.parquet",
            ],
        )
        self.assertEqual(len(http_client.uploads), 2)
        self.assertTrue(
            all(
                upload["url"].startswith(
                    "https://workspace.cloud.databricks.com/api/2.0/fs/files/"
                )
                for upload in http_client.uploads
            )
        )


if __name__ == "__main__":
    unittest.main()
