{{ config(materialized='table') }}

select
    source,
    endpoint,
    reference_date,
    ingested_at,
    crypto_ids,
    vs_currency,
    data
from read_json_auto(
    's3://bronze/market/date=*/assets=*.json',
    format = 'auto',
    union_by_name = true
)
