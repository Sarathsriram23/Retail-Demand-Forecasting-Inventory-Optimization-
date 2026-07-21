-- Data Quality Check: Duplicate Records
-- 1. Check duplicates in Calendar (Primary Key: date / d)
SELECT date, COUNT(*) as record_count
FROM calendar
GROUP BY date
HAVING COUNT(*) > 1;

-- 2. Check duplicates in Sell Prices (Primary Key: store_id, item_id, wm_yr_wk)
SELECT store_id, item_id, wm_yr_wk, COUNT(*) as record_count
FROM sell_prices
GROUP BY store_id, item_id, wm_yr_wk
HAVING COUNT(*) > 1;

-- 3. Check duplicates in Sales Train Validation (Primary Key: id / store_id + item_id)
SELECT id, COUNT(*) as record_count
FROM sales_train_validation
GROUP BY id
HAVING COUNT(*) > 1;

-- 4. Check duplicates in Sample Submission (Primary Key: id)
SELECT id, COUNT(*) as record_count
FROM sample_submission
GROUP BY id
HAVING COUNT(*) > 1;
