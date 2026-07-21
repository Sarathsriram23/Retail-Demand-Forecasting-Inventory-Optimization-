-- DDL: Calendar Dimension Table
-- Target: Google BigQuery Standard SQL / DuckDB
CREATE TABLE IF NOT EXISTS `calendar` (
    `date` DATE NOT NULL,
    `wm_yr_wk` INT64 NOT NULL,
    `weekday` STRING NOT NULL,
    `wday` INT64 NOT NULL,
    `month` INT64 NOT NULL,
    `year` INT64 NOT NULL,
    `d` STRING NOT NULL,
    `event_name_1` STRING,
    `event_type_1` STRING,
    `event_name_2` STRING,
    `event_type_2` STRING,
    `snap_CA` INT64 NOT NULL,
    `snap_TX` INT64 NOT NULL,
    `snap_WI` INT64 NOT NULL
)
-- BigQuery Partitioning & Clustering Strategy
-- PARTITION BY date;
;
