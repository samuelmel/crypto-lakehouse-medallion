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
        try_cast(json_extract_string(asset.value, '$.usd') as decimal(38, 8)) as price_usd,
        try_cast(json_extract_string(asset.value, '$.usd_market_cap') as decimal(38, 8)) as market_cap_usd,
        try_cast(json_extract_string(asset.value, '$.usd_24h_vol') as decimal(38, 8)) as total_volume_usd,
        try_cast(json_extract_string(asset.value, '$.usd_24h_change') as decimal(18, 8)) as price_change_24h,
        try_cast(json_extract_string(asset.value, '$.last_updated_at') as bigint) as source_updated_at,
        source,
        endpoint
    from bronze_snapshots,
    lateral json_each(to_json(data)) as asset
)

select *
from flattened_market
where crypto_id is not null
  and reference_date is not null
