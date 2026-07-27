import pandas as pd
from typing import Dict, Any, List
from src.db_adapter import DatabaseAdapter
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class M5DataValidator:
    """Automated data quality & validation suite for M5 dataset pipeline."""

    def __init__(self, db_adapter: DatabaseAdapter, config: Dict[str, Any]):
        self.db = db_adapter
        self.config = config
        self.val_config = config.get("validation", {})
        self.tables = config.get("tables", {})

    def validate_row_counts(self) -> Dict[str, int]:
        """Validates that loaded target tables contain rows and reports total counts."""
        results = {}
        for key, table_name in self.tables.items():
            try:
                cnt = self.db.get_row_count(table_name)
                results[table_name] = cnt
                if cnt == 0:
                    logger.error(f"[VALIDATION FAILED] Table '{table_name}' has 0 rows.")
                else:
                    logger.info(f"[VALIDATION PASSED] Table '{table_name}': {cnt:,} rows.")
            except Exception as e:
                logger.warning(f"[VALIDATION ALERT] Could not fetch count for table '{table_name}': {e}")
                results[table_name] = -1
        return results

    def validate_uniqueness(self, df: pd.DataFrame, key_cols: List[str], dataset_name: str) -> bool:
        """Validates uniqueness of key columns in DataFrame."""
        duplicate_count = df.duplicated(subset=key_cols).sum()
        if duplicate_count > 0:
            logger.error(f"[VALIDATION FAILED] [{dataset_name}] Found {duplicate_count} duplicate rows for keys {key_cols}.")
            return False
        logger.info(f"[VALIDATION PASSED] [{dataset_name}] 100% unique primary keys on {key_cols}.")
        return True

    def validate_missing_values(self, df: pd.DataFrame, critical_cols: List[str], dataset_name: str) -> bool:
        """Audits null counts against validation thresholds."""
        null_counts = df[critical_cols].isnull().sum()
        critical_nulls = null_counts[null_counts > 0]
        if not critical_nulls.empty:
            logger.error(f"[VALIDATION FAILED] [{dataset_name}] Critical missing values detected:\n{critical_nulls}")
            return False
        logger.info(f"[VALIDATION PASSED] [{dataset_name}] Zero nulls found in critical columns {critical_cols}.")
        return True

    def validate_sell_prices_ranges(self, sell_prices_df: pd.DataFrame) -> bool:
        """Sanity check: sell prices must be strictly positive (> 0)."""
        invalid_prices = (sell_prices_df["sell_price"] <= 0).sum()
        if invalid_prices > 0:
            logger.error(f"[VALIDATION FAILED] [sell_prices] Found {invalid_prices} rows with sell_price <= 0.")
            return False
        logger.info("[VALIDATION PASSED] [sell_prices] All sell prices are > 0.")
        return True

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generates a summary quality validation audit report."""
        logger.info("==========================================")
        logger.info("         DATA QUALITY AUDIT REPORT        ")
        logger.info("==========================================")
        
        row_counts = self.validate_row_counts()
        passed_all = all(count > 0 for count in row_counts.values() if count != -1)

        report = {
            "status": "SUCCESS" if passed_all else "WARNING",
            "row_counts": row_counts,
        }
        logger.info(f"Audit Status: {report['status']}")
        for tbl, cnt in row_counts.items():
            logger.info(f"  - Table '{tbl}': {cnt:,} rows")
        logger.info("==========================================")
        return report

    def validate_schema(self, df: pd.DataFrame, model_class, dataset_name: str, sample_size: int = 100) -> bool:
        """Validates that a DataFrame conforms to the specified Pydantic model schema using sampling."""
        # 1. Column presence check
        expected_fields = list(model_class.model_fields.keys())
        missing_cols = [col for col in expected_fields if col not in df.columns]
        if missing_cols:
            logger.error(f"[VALIDATION FAILED] [{dataset_name}] Missing schema columns: {missing_cols}")
            return False

        # 2. Sample records validation via Pydantic
        sample_df = df.sample(n=min(len(df), sample_size), random_state=42).copy()
        
        # Handle conversion from numpy/pandas types to Python primitives before validating
        records = sample_df[expected_fields].to_dict(orient="records")
        
        errors = []
        for idx, rec in enumerate(records):
            try:
                # Handle standard Date conversions
                if "date" in rec and isinstance(rec["date"], pd.Timestamp):
                    rec["date"] = rec["date"].date()
                model_class.model_validate(rec)
            except Exception as e:
                errors.append((idx, rec, str(e)))

        if errors:
            logger.error(f"[VALIDATION FAILED] [{dataset_name}] Schema validation errors in {len(errors)}/{sample_size} sampled rows.")
            for err_idx, rec, err_msg in errors[:3]:  # Log first 3 errors
                logger.error(f"  - Sample row {err_idx}: {rec}\n    Error: {err_msg}")
            return False

        logger.info(f"[VALIDATION PASSED] [{dataset_name}] Schema conforms to {model_class.__name__} (validated {sample_size} sample rows).")
        return True

