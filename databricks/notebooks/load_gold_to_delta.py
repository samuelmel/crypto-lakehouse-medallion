# Databricks notebook source
"""Load Gold Parquet files from a Unity Catalog Volume into Delta tables."""

from pyspark.sql import DataFrame


dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "crypto")
dbutils.widgets.text("volume", "gold")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")
base_path = f"/Volumes/{catalog}/{schema}/{volume}/gold"

TABLES = {
    "dim_cryptos": "dim_cryptos/dim_cryptos.parquet",
    "dim_calendario": "dim_calendario/dim_calendario.parquet",
    "fact_precos_mercado": "fact_precos_mercado/fact_precos_mercado.parquet",
    "agg_volatilidade_diaria": (
        "agg_volatilidade_diaria/agg_volatilidade_diaria.parquet"
    ),
}

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")


def load_delta_table(table_name: str, relative_path: str) -> int:
    """Replace one Delta table from its uploaded Gold Parquet."""
    source_path = f"{base_path}/{relative_path}"
    dataframe: DataFrame = spark.read.parquet(source_path)
    if not dataframe.columns:
        raise ValueError(f"Parquet has no columns: {source_path}")

    full_table_name = f"{catalog}.{schema}.{table_name}"
    (
        dataframe.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(full_table_name)
    )
    return dataframe.count()


load_counts = {
    table_name: load_delta_table(table_name, relative_path)
    for table_name, relative_path in TABLES.items()
}

for table_name, row_count in load_counts.items():
    print(f"Loaded {catalog}.{schema}.{table_name}: {row_count} rows")
