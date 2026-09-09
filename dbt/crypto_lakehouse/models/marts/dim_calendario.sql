{{ config(
    materialized='external',
    location='s3://gold/dim_calendario/dim_calendario.parquet',
    format='parquet'
) }}

with bounds as (
    select
        min(reference_date) as min_date,
        max(reference_date) as max_date
    from {{ ref('silver_market_prices') }}
), calendar_dates as (
    select cast(value as date) as calendar_date
    from bounds,
    generate_series(min_date, max_date, interval 1 day) as generated(value)
)

select
    cast(strftime(calendar_date, '%Y%m%d') as integer) as date_key,
    calendar_date,
    extract(year from calendar_date)::integer as year,
    extract(quarter from calendar_date)::integer as quarter,
    extract(month from calendar_date)::integer as month,
    strftime(calendar_date, '%B') as month_name,
    extract(week from calendar_date)::integer as week,
    extract(isodow from calendar_date)::integer as day_of_week,
    strftime(calendar_date, '%A') as day_name
from calendar_dates
