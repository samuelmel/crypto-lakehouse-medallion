{{ config(
    materialized='external',
    location='s3://gold/dim_cryptos/dim_cryptos.parquet',
    format='parquet'
) }}

select distinct
    crypto_id,
    upper(crypto_id) as symbol,
    crypto_id as name,
    'coingecko' as source,
    current_timestamp as created_at
from {{ ref('silver_market_prices') }}
where crypto_id is not null
