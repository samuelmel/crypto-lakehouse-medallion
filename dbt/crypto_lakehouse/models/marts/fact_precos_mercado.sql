{{ config(
    materialized='external',
    location='s3://gold/fact_precos_mercado/fact_precos_mercado.parquet',
    format='parquet'
) }}

select
    market_record_id,
    crypto_id,
    cast(strftime(reference_date, '%Y%m%d') as integer) as date_key,
    reference_date,
    ingested_at as observed_at,
    price_usd,
    market_cap_usd,
    total_volume_usd,
    price_change_24h,
    source,
    ingested_at as ingestion_timestamp
from {{ ref('silver_market_prices') }}
