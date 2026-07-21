-- DDL: Sales Train Evaluation Raw Staging Table (Wide Format d_1 .. d_1941)
-- Target: Google BigQuery Standard SQL / DuckDB
CREATE TABLE IF NOT EXISTS `sales_train_evaluation` (
    `id` STRING NOT NULL,
    `item_id` STRING NOT NULL,
    `dept_id` STRING NOT NULL,
    `cat_id` STRING NOT NULL,
    `store_id` STRING NOT NULL,
    `state_id` STRING NOT NULL
    -- Daily sales columns d_1 to d_1941 are created dynamically during table load or schema auto-detection
)
-- BigQuery Clustering Strategy:
-- CLUSTER BY store_id, item_id;
;
