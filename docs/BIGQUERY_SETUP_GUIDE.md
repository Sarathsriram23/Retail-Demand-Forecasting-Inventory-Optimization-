# Google BigQuery Setup & Configuration Guide

This guide provides step-by-step instructions for senior data engineers to set up **Google BigQuery** as the cloud data warehouse for the **Walmart M5 Retail Demand Forecasting & Inventory Optimization** project.

---

## Prerequisites

- A Google Cloud Platform (GCP) Account.
- Installed `gcloud` CLI tools (`Google Cloud SDK`).
- Python 3.10+ with `google-cloud-bigquery` library installed.

---

## Step 1: Create a Google Cloud Project

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the Project Dropdown at the top bar and select **New Project**.
3. Name your project (e.g., `retail-demand-m5-prod`).
4. Note your **Project ID** (e.g., `retail-demand-m5-prod-412300`).

Alternatively, via `gcloud` CLI:
```bash
gcloud projects create retail-demand-m5-prod --set-as-default
```

---

## Step 2: Enable BigQuery APIs

1. In the GCP Console navigation menu, go to **APIs & Services > Library**.
2. Search for **BigQuery API**.
3. Click **Enable**.

Via `gcloud` CLI:
```bash
gcloud services enable bigquery.googleapis.com bigquerystorage.googleapis.com
```

---

## Step 3: Create the BigQuery Dataset

Run the following `bq` command to create the target dataset `m5_retail_demand` in region `US`:

```bash
bq --location=US mk --dataset \
    --description "M5 Retail Demand Forecasting Data Warehouse" \
    retail-demand-m5-prod:m5_retail_demand
```

---

## Step 4: Create Service Account & Grant IAM Permissions

To allow Python ETL scripts to manage schemas and stream/load data programmatically:

1. Go to **IAM & Admin > Service Accounts**.
2. Click **Create Service Account**.
3. Name: `m5-etl-service-account`.
4. Grant the following IAM Roles:
   - **BigQuery Data Editor** (`roles/bigquery.dataEditor`)
   - **BigQuery Job User** (`roles/bigquery.jobUser`)
5. Click **Done**.

### Create & Download Service Account JSON Key
1. Click on the newly created service account.
2. Select the **Keys** tab > **Add Key** > **Create New Key**.
3. Select **JSON** format and click **Create**.
4. Save the downloaded JSON file to your local project directory:
   `config/gcp_service_account.json`

> [!CAUTION]
> Add `config/gcp_service_account.json` to your `.gitignore` file. Never commit GCP credentials to source control!

---

## Step 5: Configure `config/config.yaml`

Update the `bigquery` block in `config/config.yaml`:

```yaml
bigquery:
  project_id: "retail-demand-m5-prod"
  dataset_id: "m5_retail_demand"
  location: "US"
  credentials_file: "config/gcp_service_account.json"
```

Or set the environment variable in your terminal:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="config/gcp_service_account.json"
```

---

## Step 6: Verify Connection via Python

Test the connection using `src/db_adapter.py`:

```python
from config.logging_config import setup_logger
from src.db_adapter import DatabaseAdapter
import yaml

with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

adapter = DatabaseAdapter(config, engine_type="bigquery")
df = adapter.execute_query("SELECT 1 AS connection_test")
print(df)
```

---

## Step 7: Run BigQuery DDL Schemas & ETL Pipeline

Deploy all BigQuery tables and load the M5 dataset:

```bash
# Execute ETL targeting BigQuery
python etl/run_pipeline.py --engine bigquery

# Run Data Quality Audit
python etl/validate_pipeline.py --engine bigquery
```

---

## BigQuery Cost & Performance Optimization Summary

1. **Partitioning**: The `calendar` and `sales_fact` tables are partitioned by `date` to avoid scanning unneeded date partitions during time-series queries.
2. **Clustering**: Large tables (`sell_prices`, `sales_train_validation`, `sales_fact`) are clustered by `store_id` and `item_id` to accelerate filtering by store/category/item.
