-- DDL: Sell Prices Table
-- Target: Google BigQuery Standard SQL / DuckDB
CREATE TABLE IF NOT EXISTS `sell_prices` (
    `store_id` STRING NOT NULL,
    `item_id` STRING NOT NULL,
    `wm_yr_wk` INT64 NOT NULL,
    `sell_price` NUMERIC NOT NULL
)
-- BigQuery Clustering Strategy:
-- CLUSTER BY store_id, item_id;
;
