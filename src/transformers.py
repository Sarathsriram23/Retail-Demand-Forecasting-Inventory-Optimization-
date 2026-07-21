import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class M5DataTransformer:
    """Transforms, cleanses, deduplicates, and reshapes M5 datasets."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def deduplicate(self, df: pd.DataFrame, key_columns: List[str], dataset_name: str) -> pd.DataFrame:
        """Detects and removes duplicate records based on primary/composite key columns."""
        initial_rows = len(df)
        duplicates_count = df.duplicated(subset=key_columns).sum()

        if duplicates_count > 0:
            logger.warning(f"[{dataset_name}] Found {duplicates_count} duplicate rows on keys {key_columns}. Removing duplicates...")
            df = df.drop_duplicates(subset=key_columns, keep="first").copy()
            logger.info(f"[{dataset_name}] Deduplicated from {initial_rows} to {len(df)} rows.")
        else:
            logger.info(f"[{dataset_name}] Zero duplicates detected on key columns {key_columns}.")

        return df

    def handle_calendar_missing_values(self, calendar_df: pd.DataFrame) -> pd.DataFrame:
        """Handles missing values in calendar dataset."""
        df = calendar_df.copy()
        
        # event fields have missing values when no event occurs on that date
        event_cols = ["event_name_1", "event_type_1", "event_name_2", "event_type_2"]
        for col in event_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).replace("nan", "None").fillna("None")

        # Check required fields
        required_cols = ["date", "wm_yr_wk", "weekday", "wday", "month", "year", "d", "snap_CA", "snap_TX", "snap_WI"]
        null_counts = df[required_cols].isnull().sum()
        if null_counts.sum() > 0:
            logger.error(f"[calendar] Critical missing values detected in required columns:\n{null_counts[null_counts > 0]}")
            raise ValueError(f"[calendar] Found critical missing values in required fields.")

        logger.info("[calendar] Missing value handling completed successfully.")
        return df

    def handle_sell_prices_missing_values(self, sell_prices_df: pd.DataFrame) -> pd.DataFrame:
        """Handles missing values in sell_prices dataset."""
        df = sell_prices_df.copy()
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"[sell_prices] Missing values found:\n{null_counts[null_counts > 0]}")
            df = df.dropna(subset=["store_id", "item_id", "wm_yr_wk", "sell_price"]).copy()
            logger.info(f"[sell_prices] Dropped null rows. Remaining: {len(df)} rows.")
        else:
            logger.info("[sell_prices] Zero missing values detected.")
        return df

    def transform_sales_wide_to_long(self, sales_df: pd.DataFrame, calendar_df: pd.DataFrame, batch_size: int = 500) -> pd.DataFrame:
        """
        Unpivots (melts) wide format sales_train_validation table (30,490 rows x 1,913 days)
        into a normalized analytics fact table (id, item_id, dept_id, cat_id, store_id, state_id, d, sales_qty, date).
        """
        logger.info(f"Unpivoting sales dataframe from wide format ({sales_df.shape}) to long format...")
        
        id_vars = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
        val_vars = [col for col in sales_df.columns if col.startswith("d_")]

        # Perform melt
        long_df = sales_df.melt(
            id_vars=id_vars,
            value_vars=val_vars,
            var_name="d",
            value_name="sales_qty"
        )

        logger.info(f"Melt completed. Unpivoted rows: {len(long_df):,}")

        # Join date from calendar table
        date_map = calendar_df.set_index("d")["date"].to_dict()
        long_df["date"] = long_df["d"].map(date_map)
        long_df["sales_qty"] = long_df["sales_qty"].astype(np.int32)
        
        # Ensure date format
        long_df["date"] = pd.to_datetime(long_df["date"]).dt.date

        logger.info("Joined calendar date mapping to long sales fact dataframe.")
        return long_df
