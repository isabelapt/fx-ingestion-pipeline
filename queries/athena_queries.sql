-- =============================================================================
-- 1. DDL: External Table Creation in Amazon Athena (Data Catalog)
-- =============================================================================
CREATE EXTERNAL TABLE IF NOT EXISTS fx_rates_db_dev.raw_fx_rates (
    base_currency STRING,
    observation_date STRING,
    rates MAP<STRING, DOUBLE>
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://fx-ingestion-raw-data-dev/raw/';

-- =============================================================================
-- 2. S3 Partition Synchronization in Athena
-- =============================================================================
MSCK REPAIR TABLE fx_rates_db_dev.raw_fx_rates;

-- =============================================================================
-- 3. DML: Analytical Queries for the Trading Desk
-- =============================================================================

-- A) USD/BRL exchange rate query ordered by the most recent dates
SELECT
    observation_date,
    base_currency,
    rates['BRL'] AS usd_brl_rate
FROM fx_rates_db_dev.raw_fx_rates
WHERE year = '2026'
ORDER BY observation_date DESC;

-- B) Moving average and daily variation to identify volatility
SELECT
    observation_date,
    rates['BRL'] AS usd_brl_rate,
    AVG(rates['BRL']) OVER (
        PARTITION BY base_currency
        ORDER BY observation_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM fx_rates_db_dev.raw_fx_rates
ORDER BY observation_date DESC;