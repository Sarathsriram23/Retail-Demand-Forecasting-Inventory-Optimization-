# M5 Dataset Data Dictionary

This document describes the schema, field definitions, data types, constraints, and relationships for the **Walmart M5 Forecasting Dataset** tables in Google BigQuery / local data warehouse.

---

## Table 1: `calendar` (Dimension)

Contains date-level calendar attributes, event metadata, and SNAP (Supplemental Nutrition Assistance Program) indicators across states.

| Column Name | BigQuery Data Type | Nullable | Description / Example Values |
|---|---|---|---|
| `date` | `DATE` | No | Calendar date (`YYYY-MM-DD`). Primary Partition key. |
| `wm_yr_wk` | `INT64` | No | Walmart week ID (e.g. `11101`). Links to `sell_prices`. |
| `weekday` | `STRING` | No | Day of week (`Saturday`, `Sunday`, etc.). |
| `wday` | `INT64` | No | Day of week number (`1` = Saturday to `7` = Friday). |
| `month` | `INT64` | No | Month of year (`1` to `12`). |
| `year` | `INT64` | No | Calendar year (`2011` to `2016`). |
| `d` | `STRING` | No | Day index string (`d_1` to `d_1969`). |
| `event_name_1` | `STRING` | Yes | Name of special event occurring on date (e.g. `SuperBowl`, `Easter`). |
| `event_type_1` | `STRING` | Yes | Category of event 1 (`Sporting`, `Cultural`, `National`, `Religious`). |
| `event_name_2` | `STRING` | Yes | Name of secondary event occurring on date. |
| `event_type_2` | `STRING` | Yes | Category of secondary event 2. |
| `snap_CA` | `INT64` | No | Binary indicator (`0` or `1`) if SNAP purchases are allowed in CA on date. |
| `snap_TX` | `INT64` | No | Binary indicator (`0` or `1`) if SNAP purchases are allowed in TX on date. |
| `snap_WI` | `INT64` | No | Binary indicator (`0` or `1`) if SNAP purchases are allowed in WI on date. |

---

## Table 2: `sell_prices` (Dimension / Price History)

Contains historical selling prices per item, per store, per Walmart week.

| Column Name | BigQuery Data Type | Nullable | Description / Example Values |
|---|---|---|---|
| `store_id` | `STRING` | No | Store identifier (`CA_1`, `CA_2`, `TX_1`, `WI_1`, etc.). Cluster key. |
| `item_id` | `STRING` | No | Item identifier (e.g., `HOBBIES_1_001`). Cluster key. |
| `wm_yr_wk` | `INT64` | No | Walmart week ID (e.g., `11325`). Foreign key to `calendar`. |
| `sell_price` | `NUMERIC` | No | Price of product in USD (must be > 0). |

---

## Table 3: `sales_train_validation` (Staging - Wide Format)

Contains historical unit sales per product/store for days `d_1` through `d_1913`.

| Column Name | BigQuery Data Type | Nullable | Description |
|---|---|---|---|
| `id` | `STRING` | No | Unique series ID (e.g. `HOBBIES_1_001_CA_1_validation`). |
| `item_id` | `STRING` | No | Item ID. |
| `dept_id` | `STRING` | No | Department ID (`HOBBIES_1`, `FOODS_3`, `HOUSEHOLD_2`). |
| `cat_id` | `STRING` | No | Category ID (`HOBBIES`, `FOODS`, `HOUSEHOLD`). |
| `store_id` | `STRING` | No | Store ID (`CA_1`, `CA_2`, `TX_1`, `WI_1`, etc.). |
| `state_id` | `STRING` | No | State ID (`CA`, `TX`, `WI`). |
| `d_1` .. `d_1913` | `INT64` | Yes | Daily sales quantities for day 1 through day 1913. |

---

## Table 4: `sales_train_evaluation` (Staging - Wide Format)

Contains historical unit sales per product/store for days `d_1` through `d_1941`.

| Column Name | BigQuery Data Type | Nullable | Description |
|---|---|---|---|
| `id` | `STRING` | No | Unique series ID (e.g. `HOBBIES_1_001_CA_1_evaluation`). |
| `item_id` .. `state_id` | `STRING` | No | Categorical hierarchy levels. |
| `d_1` .. `d_1941` | `INT64` | Yes | Daily sales quantities for day 1 through day 1941. |

---

## Table 5: `sample_submission` (Submission Format)

Template structure for model forecasts.

| Column Name | BigQuery Data Type | Nullable | Description |
|---|---|---|---|
| `id` | `STRING` | No | Series ID (`..._validation` or `..._evaluation`). |
| `F1` .. `F28` | `INT64` | Yes | Forecasted sales values for 28 forecast horizon days. |

---

## Table 6: `sales_fact` (Analytics Fact Table - Unpivoted / Long Format)

Unpivoted, normalized time-series analytics table for demand modeling & inventory reporting.

| Column Name | BigQuery Data Type | Nullable | Description / Key Role |
|---|---|---|---|
| `id` | `STRING` | No | Unique series identifier. |
| `item_id` | `STRING` | No | Product identifier (Cluster Key). |
| `dept_id` | `STRING` | No | Department identifier. |
| `cat_id` | `STRING` | No | Category identifier. |
| `store_id` | `STRING` | No | Store location identifier (Cluster Key). |
| `state_id` | `STRING` | No | State location identifier. |
| `d` | `STRING` | No | Day index string (`d_1` .. `d_1913`). |
| `date` | `DATE` | No | Calendar date (`YYYY-MM-DD`). Partition Key. |
| `sales_qty` | `INT64` | No | Unit sales quantity. |
