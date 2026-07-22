import argparse
import sys
import yaml
import time
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logger
from src.db_adapter import DatabaseAdapter
from src.extractors import M5DataExtractor
from src.transformers import M5DataTransformer
from src.loaders import M5DataLoader
from src.validators import M5DataValidator

logger = setup_logger(__name__)

def load_config(config_path: str) -> dict:
    """Loads YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_etl(config_path: str = "config/config.yaml", engine_override: str = None):
    """Executes full M5 Data Engineering ETL pipeline."""
    start_time = time.time()
    logger.info("=========================================================================")
    logger.info("  STARTING WEEK 1 M5 RETAIL DEMAND FORECASTING ETL PIPELINE EXECUTION    ")
    logger.info("=========================================================================")

    # 1. Load Configuration
    config = load_config(config_path)
    if engine_override:
        config["pipeline"]["default_engine"] = engine_override

    engine_type = config["pipeline"]["default_engine"]
    logger.info(f"Target Database Engine: {engine_type.upper()}")

    # 2. Database Adapter & Schema Setup
    db_adapter = DatabaseAdapter(config, engine_type=engine_type)
    loader = M5DataLoader(db_adapter, config)
    logger.info("Initializing database schemas (DDL execution)...")
    loader.initialize_schemas()

    # 3. Component Instances
    extractor = M5DataExtractor(config)
    transformer = M5DataTransformer(config)
    validator = M5DataValidator(db_adapter, config)

    # 4. Pipeline Execution: Calendar
    logger.info("--- Step 4.1: Processing Calendar Dimension ---")
    cal_raw = extractor.extract_calendar()
    validator.validate_uniqueness(cal_raw, key_cols=["date"], dataset_name="calendar")
    validator.validate_uniqueness(cal_raw, key_cols=["d"], dataset_name="calendar")
    cal_clean = transformer.deduplicate(cal_raw, key_columns=["d"], dataset_name="calendar")
    cal_clean = transformer.handle_calendar_missing_values(cal_clean)
    validator.validate_missing_values(cal_clean, critical_cols=["date", "wm_yr_wk", "d"], dataset_name="calendar")
    loader.load_calendar(cal_clean, if_exists="replace")

    # 5. Pipeline Execution: Sell Prices
    logger.info("--- Step 4.2: Processing Sell Prices Dimension ---")
    prices_raw = extractor.extract_sell_prices(chunked=False)
    validator.validate_uniqueness(prices_raw, key_cols=["store_id", "item_id", "wm_yr_wk"], dataset_name="sell_prices")
    prices_clean = transformer.deduplicate(prices_raw, key_columns=["store_id", "item_id", "wm_yr_wk"], dataset_name="sell_prices")
    prices_clean = transformer.handle_sell_prices_missing_values(prices_clean)
    validator.validate_sell_prices_ranges(prices_clean)
    loader.load_sell_prices(prices_clean, if_exists="replace")

    # 6. Pipeline Execution: Sales Train Validation (Raw Staging)
    logger.info("--- Step 4.3: Processing Sales Train Validation (Staging) ---")
    sales_val_raw = extractor.extract_sales_validation()
    validator.validate_uniqueness(sales_val_raw, key_cols=["id"], dataset_name="sales_train_validation")
    sales_val_clean = transformer.deduplicate(sales_val_raw, key_columns=["id"], dataset_name="sales_train_validation")
    loader.load_sales_train_validation(sales_val_clean, if_exists="replace")

    # 7. Pipeline Execution: Sales Train Evaluation (Raw Staging)
    logger.info("--- Step 4.4: Processing Sales Train Evaluation (Staging) ---")
    sales_eval_raw = extractor.extract_sales_evaluation()
    if not sales_eval_raw.empty:
        validator.validate_uniqueness(sales_eval_raw, key_cols=["id"], dataset_name="sales_train_evaluation")
        sales_eval_clean = transformer.deduplicate(sales_eval_raw, key_columns=["id"], dataset_name="sales_train_evaluation")
        loader.load_sales_train_evaluation(sales_eval_clean, if_exists="replace")

    # 8. Pipeline Execution: Sample Submission
    logger.info("--- Step 4.5: Processing Sample Submission ---")
    sub_raw = extractor.extract_sample_submission()
    validator.validate_uniqueness(sub_raw, key_cols=["id"], dataset_name="sample_submission")
    sub_clean = transformer.deduplicate(sub_raw, key_columns=["id"], dataset_name="sample_submission")
    loader.load_sample_submission(sub_clean, if_exists="replace")

    # 9. Pipeline Execution: Sales Fact Transformation (Wide to Long Analytics Table)
    logger.info("--- Step 4.6: Building Normalized Sales Fact Analytical Table ---")
    chunk_generator = transformer.transform_sales_wide_to_long_chunks(sales_val_clean, cal_clean, chunk_size=5000)
    
    first_chunk = True
    for chunk in chunk_generator:
        validator.validate_missing_values(chunk, critical_cols=["id", "item_id", "store_id", "date", "sales_qty"], dataset_name="sales_fact_chunk")
        if_exists = "replace" if first_chunk else "append"
        loader.load_sales_fact(chunk, if_exists=if_exists)
        first_chunk = False


    # 10. Automated Data Quality Audit Report
    logger.info("--- Step 5: Data Quality Verification Audit ---")
    audit_report = validator.generate_quality_report()

    # Close connections
    db_adapter.close()

    elapsed = time.time() - start_time
    logger.info("=========================================================================")
    logger.info(f"  ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS          ")
    logger.info("=========================================================================")
    return audit_report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Week 1 M5 Retail Demand ETL Pipeline")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config YAML file")
    parser.add_argument("--engine", type=str, choices=["duckdb", "bigquery"], help="Override default database engine")
    args = parser.parse_args()

    run_etl(config_path=args.config, engine_override=args.engine)
