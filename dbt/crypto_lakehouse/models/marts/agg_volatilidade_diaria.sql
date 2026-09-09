{{ config(
    materialized='external',
    location='s3://gold/agg_volatilidade_diaria/agg_volatilidade_diaria.parquet',
    format='parquet'
) }}

with daily_prices as (
    select
        crypto_id,
        reference_date,
        min(price_usd) as minimum_price_usd,
        max(price_usd) as maximum_price_usd,
        avg(price_usd) as average_price_usd,
        arg_min(price_usd, ingested_at) as opening_price_usd,
        arg_max(price_usd, ingested_at) as closing_price_usd,
        stddev_samp(price_usd) as sample_volatility
    from {{ ref('silver_market_prices') }}
    group by crypto_id, reference_date
)

select
    md5(concat(crypto_id, ':', reference_date::varchar)) as volatility_id,
    crypto_id,
    cast(strftime(reference_date, '%Y%m%d') as integer) as date_key,
    opening_price_usd,
    closing_price_usd,
    minimum_price_usd,
    maximum_price_usd,
    average_price_usd,
    (closing_price_usd - opening_price_usd)
        / nullif(opening_price_usd, 0) as daily_return,
    coalesce(sample_volatility, 0) as volatility,
    current_timestamp as calculated_at
from daily_prices
