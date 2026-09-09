"""Airflow DAG for the daily CoinGecko Bronze snapshot."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion.coingecko_bronze import BronzeConfig, ingest_market_data


def run_bronze_ingestion() -> str:
    """Fetch the configured assets and write the Bronze object."""
    object_key = ingest_market_data(BronzeConfig.from_environment())
    print(f"Bronze object written: {object_key}")
    return object_key


with DAG(
    dag_id="crypto_bronze_ingestion",
    description="Daily idempotent CoinGecko snapshot into MinIO Bronze",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["crypto", "bronze", "coingecko"],
) as dag:
    ingest_bronze = PythonOperator(
        task_id="ingest_market_snapshot",
        python_callable=run_bronze_ingestion,
    )
