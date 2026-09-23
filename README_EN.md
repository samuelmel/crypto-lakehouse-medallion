[🇧🇷 Português](README.md) | 🇺🇸 English

<div align="center">

# 🚀 Crypto Lakehouse

### *Cryptocurrency Data Lakehouse with Medallion Architecture (Bronze, Silver, Gold)*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![dbt](https://img.shields.io/badge/dbt--core-1.8%2B-brightgreen.svg)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.1%2B-orange.svg)](https://duckdb.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.10%2B-017CEE.svg)](https://airflow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A cryptocurrency Data Lakehouse built to collect, process, transform, and make market data available in an automated, testable, and structured way for advanced analytics.**

</div>

---

## 🌟 Key Features

### 1. 🥉 Medallion Architecture — Bronze → Silver → Gold

The project implements a layered data architecture, separating ingestion, transformation, and analytical consumption.

* **Bronze:** idempotent ingestion of raw data from the CoinGecko API into **MinIO**, using S3-compatible storage and deterministic keying.
* **Silver:** flattening, strict typing, and transformation of data into **Parquet** using **dbt + DuckDB**.
* **Gold:** dimensional modeling using a **Star Schema**, with fact tables, dimensions, and daily volatility aggregations.

This separation keeps raw data preserved while allowing the following layers to be transformed and rebuilt in a controlled manner.

### 2. ⚙️ Apache Airflow Orchestration

The pipeline is automated using **Apache Airflow**.

* DAGs for Bronze layer ingestion.
* Silver → Gold transformation pipeline.
* Upload of Gold data to Databricks.
* Configurable retries.
* Timeouts.
* Detailed logs.
* Concurrent execution control.
* Monitoring and manual pipeline triggering through the Airflow web interface.

### 3. 🧠 Transformation with dbt + DuckDB

Data transformation is performed using **dbt** and **DuckDB**, allowing SQL models to be executed locally and reproducibly.

* SQL models organized by layer.
* Tests for `not_null`, `unique`, and `relationships`.
* Direct reading of data stored in S3 through DuckDB's `httpfs` extension.
* Silver and Gold layers materialized as **Parquet**.
* Ability to execute and test models locally before running the complete orchestration.

### 4. ☁️ Cloud Integration with Databricks

The Gold layer can be integrated with a cloud environment using **Databricks**.

* Automatic upload of Gold Parquet files.
* Integration with **Unity Catalog / Volumes**.
* **PySpark** notebook for converting data into Delta Tables.
* Structure prepared for exploring governance and security concepts in cloud environments.

### 5. 🧪 Automated Testing

The project contains tests at different levels to validate both the application and data quality.

* Python unit tests using `unittest`.
* Mocks for S3 and HTTP services.
* Data quality tests using dbt.
* Validation of uniqueness, non-nullability, and relationships.
* Idempotency tests.
* Controlled reprocessing validation.

---

## 📌 Why This Project?

Crypto Lakehouse was developed to demonstrate, within a single project, a Data Engineering workflow close to a real-world scenario.

* **Modern Stack:** Docker, Apache Airflow, dbt, DuckDB, MinIO, and Databricks.
* **Reproducibility:** environment defined through Docker Compose and environment variables.
* **Data Quality:** automated validations during transformations.
* **Idempotency:** ability to reprocess data without generating unintended duplicates.
* **Separation of Responsibilities:** ingestion, transformation, storage, and consumption are organized into layers.
* **Scalability:** the Gold layer is structured for later consumption by BI, Machine Learning, or Data Science tools.
* **Local + Cloud Integration:** the project allows working with a local Data Lake and subsequently making the data available in Databricks.
* **Best Practices:** error handling, automated testing, responsibility-based organization, and reproducible pipelines.

---

## 🏗️ Architecture

Crypto Lakehouse implements a complete Data Engineering workflow, from ingesting data from CoinGecko to making information available in the Gold layer and integrating with Databricks.

<div align="center">

<img src="img/CoinGecko%20API%20Ingestion-2026-09-09-001131.png" alt="CoinGecko API Ingestion" width="900">

<p><em>CoinGecko market data ingestion flow into the Bronze layer.</em></p>

</div>

```text
                         ┌──────────────────────┐
                         │      CoinGecko       │
                         │       REST API       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       BRONZE         │
                         │       MinIO/S3       │
                         │                      │
                         │   Raw JSON Data      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        SILVER        │
                         │     dbt + DuckDB     │
                         │                      │
                         │  Flatten + Typing    │
                         │       Parquet        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │         GOLD         │
                         │     Star Schema      │
                         │                      │
                         │ Facts + Dimensions   │
                         │ Daily Aggregations   │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
             ┌───────────────┐             ┌───────────────┐
             │   Databricks   │             │   Analytics   │
             │ Unity Catalog  │             │  BI / ML / DS │
             │ Delta Tables   │             └───────────────┘
             └───────────────┘
```

<div align="center">

<img src="img/Untitled.png" alt="Crypto Lakehouse Architecture" width="900">

<p><em>Overall Data Lakehouse architecture and data processing flow.</em></p>

</div>

Pipeline execution and dependencies are orchestrated by **Apache Airflow**, while local storage uses **MinIO** and SQL transformations use **dbt + DuckDB**.

The main flow can be summarized as:

**CoinGecko API → Bronze → Silver → Gold → Databricks / Analytics**

---

## ⚡ Quickstart

### 1. Installing Dependencies

It is recommended to use [`uv`](https://github.com/astral-sh/uv) for its fast dependency resolution and installation, but the project can also be run using `pip`.

```bash
# Clone the repository

git clone https://github.com/your-username/crypto-lakehouse.git

cd crypto-lakehouse

# Using uv

uv venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

uv pip install -r requirements.txt
```

Or using `pip`:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Configure the variables required for the local environment and the services used by the project.

### 3. Start the Infrastructure

Start the containers using Docker Compose:

```bash
docker compose up -d --build
```

The local infrastructure includes the services required to run the pipeline, including MinIO, PostgreSQL, and Airflow.

After startup:

* **Airflow:** `http://localhost:8080`
* **MinIO Console:** `http://localhost:9001`

Default local environment credentials:

```text
Airflow
Username: admin
Password: admin

MinIO
Username: minioadmin
Password: minioadmin
```

> The credentials above are intended for the local development environment.

### 4. Run dbt Locally

Synchronize the environment:

```bash
uv sync
```

Configure the dbt profile:

```bash
mkdir -p ~/.dbt

cp dbt/profiles.yml ~/.dbt/
```

Validate the configuration:

```bash
uv run dbt debug --profiles-dir ~/.dbt
```

Run the models individually:

```bash
# Staging / Bronze
uv run dbt run \
  --select stg_bronze_market \
  --profiles-dir ~/.dbt

# Silver
uv run dbt run \
  --select silver_market_prices \
  --profiles-dir ~/.dbt

# Gold
uv run dbt build \
  --select +marts \
  --profiles-dir ~/.dbt
```

### 5. Run the Tests

```bash
uv run python -m unittest \
  tests.test_coingecko_bronze \
  tests.test_databricks_upload \
  -v
```

Or run the complete pipeline through the Airflow interface:

```text
http://localhost:8080
```

---

## 💻 Transformation Example — dbt + DuckDB

The `silver_market_prices.sql` model demonstrates the transformation of raw CoinGecko data into a typed tabular structure stored as Parquet.

```sql
{{ config(
    materialized='external',
    location='s3://silver/market/silver_market_prices.parquet',
    format='parquet'
) }}

with bronze_snapshots as (

    select
        source,
        endpoint,
        reference_date::date as reference_date,
        ingested_at::timestamp as ingested_at,
        vs_currency,
        data

    from {{ ref('stg_bronze_market') }}

),

flattened_market as (

    select

        md5(
            concat(
                reference_date::varchar,
                ':',
                asset.key,
                ':',
                vs_currency
            )
        ) as market_record_id,

        asset.key as crypto_id,

        reference_date,
        ingested_at,
        vs_currency,

        try_cast(
            json_extract_string(asset.value, '$.usd')
            as decimal(38, 8)
        ) as price_usd,

        try_cast(
            json_extract_string(asset.value, '$.usd_market_cap')
            as decimal(38, 8)
        ) as market_cap_usd,

        try_cast(
            json_extract_string(asset.value, '$.usd_24h_vol')
            as decimal(38, 8)
        ) as total_volume_usd,

        try_cast(
            json_extract_string(asset.value, '$.usd_24h_change')
            as decimal(18, 8)
        ) as price_change_24h,

        try_cast(
            json_extract_string(asset.value, '$.last_updated_at')
            as bigint
        ) as source_updated_at,

        source,
        endpoint

    from bronze_snapshots,

    lateral json_each(to_json(data)) as asset

)

select *

from flattened_market

where crypto_id is not null
  and reference_date is not null
```

The model flattens the JSON received from CoinGecko, generates a deterministic identifier for the records, and converts the main market indicators into appropriate numeric types.

---

## 🔎 Example Queries

### Silver — Price and Volume

```sql
SELECT
    crypto_id,
    reference_date,
    price_usd,
    market_cap_usd,
    total_volume_usd,
    price_change_24h

FROM silver_market_prices

ORDER BY reference_date DESC, ingested_at DESC

LIMIT 10;
```

### Gold — Price History

```sql
SELECT
    d.symbol,
    f.reference_date,
    f.price_usd,
    f.market_cap_usd,
    f.total_volume_usd

FROM fact_precos_mercado f

JOIN dim_cryptos d
    USING (crypto_id)

ORDER BY f.reference_date DESC

LIMIT 20;
```

### Gold — Daily Volatility and Return

```sql
SELECT
    d.symbol,
    v.reference_date,
    v.opening_price_usd,
    v.closing_price_usd,
    v.daily_return,
    v.volatility

FROM agg_volatilidade_diaria v

JOIN dim_cryptos d
    USING (crypto_id)

ORDER BY v.reference_date DESC, v.volatility DESC;
```

---

## 🛠️ Technologies Used

| Category               | Technology               | Usage                                                        |
| ---------------------- | ------------------------ | ------------------------------------------------------------ |
| **Orchestration**      | Apache Airflow 2.10+     | DAGs, retries, trigger rules, pools, and concurrency control |
| **Storage**            | MinIO                    | S3-compatible Object Storage                                 |
| **Transformation**     | dbt-core + dbt-duckdb    | SQL modeling and data quality testing                        |
| **Query Engine**       | DuckDB 1.1+              | Analytical processing and Parquet/S3 querying                |
| **Cloud Lakehouse**    | Databricks Unity Catalog | Volumes, Delta Tables, and PySpark notebooks                 |
| **Ingestion**          | Python + requests        | CoinGecko API consumption                                    |
| **Containers**         | Docker Compose           | Local infrastructure execution                               |
| **Package Management** | uv / pip                 | Python environments and dependencies                         |
| **Analysis**           | Pandas / PyArrow         | Additional exploration and notebooks                         |

---

## 🧪 Automated Testing

### Unit Tests

Python tests validate components related to CoinGecko ingestion and Databricks uploads.

```bash
uv run python -m unittest \
  tests.test_coingecko_bronze \
  tests.test_databricks_upload \
  -v
```

### dbt Data Quality Tests

Validation of model integrity, uniqueness, and relationships:

```bash
uv run dbt test --profiles-dir dbt/
```

### Full Build

Runs the models and tests sequentially:

```bash
uv run dbt build --profiles-dir dbt/
```

---

## 📂 Project Structure

```text
crypto-lakehouse/
│
├── img/
│   ├── CoinGecko API Ingestion-2026-09-09-001131.png
│   └── Untitled.png
│
├── dags/
│   ├── bronze/
│   ├── silver_gold/
│   └── databricks/
│
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── silver/
│   │   └── marts/
│   ├── tests/
│   └── profiles.yml
│
├── src/
│   ├── ingestion/
│   ├── databricks/
│   └── ...
│
├── tests/
│
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🎯 Concepts Demonstrated

This project explores concepts relevant to modern Data Engineering:

* Medallion Architecture.
* Data Lakes and Lakehouses.
* ETL/ELT.
* S3-compatible Object Storage.
* Analytical processing with DuckDB.
* Transformations and testing with dbt.
* Orchestration with Apache Airflow.
* Parquet format.
* Dimensional modeling and Star Schema.
* Idempotency and reprocessing.
* Data Quality.
* Automated testing.
* Integration between local infrastructure and cloud environments.
* Databricks, Unity Catalog, and Delta Tables.
* Containerization with Docker.

---

## 👨‍💻 Author

**Samuel Santos**

This project was developed as a **technical portfolio and study project**, focused on Data Engineering, modern data architectures, automation, and software engineering best practices.

Crypto Lakehouse explores concepts such as:

* Medallion Architecture and Lakehouses.
* ELT with dbt and open-source tools.
* Workflow orchestration with Apache Airflow.
* Integration between local Data Lakes and cloud platforms.
* Databricks and PySpark processing.
* Testability and data quality in Data Engineering pipelines.

---

## 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for more information.

---

[🇧🇷 Português](README.md) | 🇺🇸 English
