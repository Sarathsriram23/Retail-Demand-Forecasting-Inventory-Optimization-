# Retail Demand Forecasting & Inventory Optimization - Week 1 Data Engineering Pipeline

![Data Engineering Pipeline](https://img.shields.io/badge/Architecture-BigQuery%20%7C%20DuckDB-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![Dataset](https://img.shields.io/badge/Dataset-Walmart%20M5-orange)

## Executive Summary

This repository contains the complete **Week 1 Data Engineering Implementation** for the **Retail Demand Forecasting & Inventory Optimization** system built on the **Walmart M5 Forecasting Dataset**.

The primary objective of Week 1 is to establish a robust, production-ready, cloud-native data architecture in **Google BigQuery** (with a zero-dependency **DuckDB local engine fallback**), create standard SQL DDL schemas, build modular Python ETL pipelines with logging, enforce automated data quality checks, handle duplicate records, audit missing values, and transform wide daily sales metrics into a normalized star-schema analytics table.

---

## Key Achievements & Delivered Components

1. **Folder Architecture**: Enterprise-grade modular data engineering repository structure.
2. **Dual Engine Adapter (`db_adapter.py`)**: Seamlessly runs on **Google BigQuery** in production and **DuckDB / SQLite** locally without requiring GCP cloud credentials for testing.
3. **SQL Schemas (DDL)**: BigQuery DDL scripts for all 5 M5 dataset tables (`calendar`, `sell_prices`, `sales_train_validation`, `sales_train_evaluation`, `sample_submission`), plus an unpivoted analytics fact table (`sales_fact`) with `date` partitioning and `store_id`, `item_id` clustering.
4. **Python ETL Engine**:
   - `extractors.py`: Efficient chunked CSV loading.
   - `transformers.py`: Key deduplication, missing value handling, wide-to-long melting.
   - `loaders.py`: High-performance bulk database loading.
   - `validators.py`: Data quality verification suite (row counts, null audits, range checks).
5. **Data Quality Suite**:
   - Duplicate Detection: Composite key deduplication (`date`, `store_id + item_id + wm_yr_wk`, `id`).
   - Missing Value Handling: Event name imputation (`None`), null count assertions on critical fields.
   - Range Checks: `sell_price > 0` validation.
6. **Structured Logging**: Timestamps, log levels, component tracking output to console and `logs/etl_pipeline.log`.
7. **Comprehensive Documentation**: `BIGQUERY_SETUP_GUIDE.md`, `DATA_DICTIONARY.md`, and unit test suite.

---

## Directory Structure

```
Retail Demand Forecasting & Inventory/
├── config/
│   ├── config.yaml               # Pipeline settings, BigQuery & DuckDB settings, dataset paths
│   └── logging_config.py         # Structured logging configuration (file + console)
├── sql/
│   ├── ddl/
│   │   ├── 01_create_calendar.sql
│   │   ├── 02_create_sell_prices.sql
│   │   ├── 03_create_sales_train_validation.sql
│   │   ├── 04_create_sales_train_evaluation.sql
│   │   ├── 05_create_sample_submission.sql
│   │   └── 06_create_sales_fact.sql
│   └── quality_checks/
│       ├── check_duplicates.sql
│       └── check_missing_values.sql
├── src/
│   ├── __init__.py
│   ├── db_adapter.py             # BigQuery + DuckDB dual engine database adapter
│   ├── extractors.py             # Memory-optimized dataset loaders & generators
│   ├── transformers.py          # Cleaning, deduplication, missing value handling, wide-to-long melt
│   ├── loaders.py                # Database table loading management
│   └── validators.py            # Data quality assertion & audit report engine
├── etl/
│   ├── __init__.py
│   ├── run_pipeline.py           # Main ETL execution script
│   └── validate_pipeline.py     # Standalone data quality validation runner
├── docs/
│   ├── BIGQUERY_SETUP_GUIDE.md   # GCP setup, service account key, IAM, and BigQuery creation guide
│   └── DATA_DICTIONARY.md        # Comprehensive dataset column definitions and types
├── tests/
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_transformers.py
│   └── test_validators.py
├── m5-forecasting-accuracy/       # Dataset CSV directory
├── requirements.txt              # Dependency definitions
└── README.md                     # Senior Data Engineer Week 1 Documentation
```

---

## Quick Start & Installation

### 1. Clone & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Pipeline Settings
Edit `config/config.yaml` to specify target settings:
- Default database engine: `duckdb` (local) or `bigquery` (cloud).
- Dataset CSV file paths.

---

## Executing the ETL Pipeline

### Run Full ETL (Local DuckDB Engine)
```bash
python etl/run_pipeline.py --engine duckdb
```

### Run Full ETL (Google BigQuery Engine)
Ensure your service account key is saved to `config/gcp_service_account.json` or `GOOGLE_APPLICATION_CREDENTIALS` is set:
```bash
python etl/run_pipeline.py --engine bigquery
```

### Run Standalone Data Quality Audit
```bash
python etl/validate_pipeline.py --engine duckdb
```

### Run Unit Test Suite
```bash
pytest tests/
```

### Launch the Streamlit Dashboard
```bash
streamlit run app.py
```

The dashboard includes store/category filters, historical sales charts, forecast comparison, and a simple what-if inventory simulation.

---

## Data Schema & Optimization Rationale

- **Calendar Table**: Partitioned by `date` (DATE) to accelerate time-slice filters.
- **Sell Prices Table**: Clustered by `store_id` and `item_id` to allow ultra-fast lookup during price elasticity modeling.
- **Sales Fact Table**: Unpivoted from 1,913 day columns (`d_1`..`d_1913`) into a long-format star schema table (`id`, `item_id`, `dept_id`, `cat_id`, `store_id`, `state_id`, `d`, `sales_qty`, `date`), partitioned by `date` and clustered by `store_id`, `item_id`.

---

## Logging & Monitoring

ETL events, metrics, row counts, warnings, and validation audits are logged automatically to `logs/etl_pipeline.log` with standard format:

```text
[2026-07-21 21:30:00] [INFO] [src.extractors:extract_calendar:22] - Loaded calendar dataset: 1969 rows, 14 columns.
[2026-07-21 21:30:01] [INFO] [src.transformers:deduplicate:24] - [calendar] Zero duplicates detected on key columns ['d'].
[2026-07-21 21:30:05] [INFO] [src.loaders:load_calendar:28] - Successfully loaded 1969 rows into table 'calendar'.
```

---

## License & Dataset Attribution

The M5 Forecasting Dataset is provided by Walmart and Kaggle for research and competition purposes.
