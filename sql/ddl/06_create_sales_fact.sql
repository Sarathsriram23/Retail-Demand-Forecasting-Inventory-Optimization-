-- DDL: Sales Fact Normalized Analytics Table (Unpivoted / Long Format)
-- Target: Google BigQuery Standard SQL / DuckDB
CREATE TABLE IF NOT EXISTS `sales_fact` (
    `id` STRING NOT NULL,
    `item_id` STRING NOT NULL,
    `dept_id` STRING NOT NULL,
    `cat_id` STRING NOT NULL,
    `store_id` STRING NOT NULL,
    `state_id` STRING NOT NULL,
    `d` STRING NOT NULL,
    `date` DATE NOT NULL,
    `sales_qty` INT64 NOT NULL
)
-- BigQuery Partitioning & Clustering Strategy:
-- PARTITION BY date
-- CLUSTER BY store_id, item_id;
;
