"""End-to-end Crypto Lakehouse orchestration DAG."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from ingestion.coingecko_bronze import BronzeConfig, ingest_market_data

DBT_PROJECT_DIR = "/opt/airflow/dbt/crypto_lakehouse"
DBT_PROFILES_DIR = "/opt/airflow/dbt"


def run_bronze_ingestion() -> str:
    """Fetch the configured assets and write the deterministic Bronze object."""
    object_key = ingest_market_data(BronzeConfig.from_environment())
    print(f"Bronze object written: {object_key}")
    return object_key


DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="crypto_lakehouse_pipeline",
    description="End-to-end Bronze, Silver and Gold Crypto Lakehouse pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
    default_args=DEFAULT_ARGS,
    tags=["crypto", "lakehouse", "medallion", "end-to-end"],
) as dag:
    ingest_bronze = PythonOperator(
        task_id="ingest_bronze",
        python_callable=run_bronze_ingestion,
        execution_timeout=timedelta(minutes=5),
    )

    build_silver = BashOperator(
        task_id="build_silver",
        bash_command=(
            "set -euo pipefail; "
            f"dbt run --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            "--select stg_bronze_market silver_market_prices"
        ),
        execution_timeout=timedelta(minutes=10),
    )

    test_silver = BashOperator(
        task_id="test_silver",
        bash_command=(
            "set -euo pipefail; "
            f"dbt test --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            "--select silver_market_prices"
        ),
        execution_timeout=timedelta(minutes=10),
    )

    build_gold = BashOperator(
        task_id="build_gold",
        bash_command=(
            "set -euo pipefail; "
            f"dbt build --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            "--select +marts"
        ),
        execution_timeout=timedelta(minutes=15),
    )

    ingest_bronze >> build_silver >> test_silver >> build_gold
