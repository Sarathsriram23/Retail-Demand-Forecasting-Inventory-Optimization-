-- Data Quality Check: Missing Values Audit
-- 1. Check NULL values in Calendar Table
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) as null_date,
    SUM(CASE WHEN wm_yr_wk IS NULL THEN 1 ELSE 0 END) as null_wm_yr_wk,
    SUM(CASE WHEN d IS NULL THEN 1 ELSE 0 END) as null_d,
    SUM(CASE WHEN event_name_1 IS NULL THEN 1 ELSE 0 END) as null_event_name_1,
    SUM(CASE WHEN event_type_1 IS NULL THEN 1 ELSE 0 END) as null_event_type_1,
    SUM(CASE WHEN event_name_2 IS NULL THEN 1 ELSE 0 END) as null_event_name_2,
    SUM(CASE WHEN event_type_2 IS NULL THEN 1 ELSE 0 END) as null_event_type_2
FROM calendar;

-- 2. Check NULL values in Sell Prices Table
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN store_id IS NULL THEN 1 ELSE 0 END) as null_store_id,
    SUM(CASE WHEN item_id IS NULL THEN 1 ELSE 0 END) as null_item_id,
    SUM(CASE WHEN wm_yr_wk IS NULL THEN 1 ELSE 0 END) as null_wm_yr_wk,
    SUM(CASE WHEN sell_price IS NULL THEN 1 ELSE 0 END) as null_sell_price
FROM sell_prices;

-- 3. Check NULL values in Sales Staging Table Key Identifiers
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_id,
    SUM(CASE WHEN item_id IS NULL THEN 1 ELSE 0 END) as null_item_id,
    SUM(CASE WHEN store_id IS NULL THEN 1 ELSE 0 END) as null_store_id
FROM sales_train_validation;
