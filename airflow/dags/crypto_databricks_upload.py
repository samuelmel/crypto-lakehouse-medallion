"""Airflow DAG for uploading Gold Parquet files to Databricks Volumes."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from databricks.upload_gold import DatabricksUploadConfig, upload_gold_files


def upload_gold_to_databricks() -> list[str]:
    """Upload local Gold objects to the configured Unity Catalog Volume."""
    uploaded_paths = upload_gold_files(DatabricksUploadConfig.from_environment())
    print(f"Uploaded {len(uploaded_paths)} Gold files to Databricks")
    return uploaded_paths


with DAG(
    dag_id="crypto_databricks_upload",
    description="Upload idempotent Gold Parquet files to Databricks Volumes",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["crypto", "databricks", "gold"],
) as dag:
    upload_gold = PythonOperator(
        task_id="upload_gold_to_databricks",
        python_callable=upload_gold_to_databricks,
        execution_timeout=timedelta(minutes=20),
    )
