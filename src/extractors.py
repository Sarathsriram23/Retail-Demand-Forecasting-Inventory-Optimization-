import os
import pandas as pd
from typing import Dict, Any, Generator, Optional
from pathlib import Path
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class M5DataExtractor:
    """Extracts raw M5 dataset CSV files with memory-optimized chunking and type casting."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_paths = config.get("data_paths", {})
        self.chunk_size = config.get("pipeline", {}).get("chunk_size", 50000)

    def extract_calendar(self) -> pd.DataFrame:
        """Extracts calendar.csv dimension table."""
        file_path = self.data_paths.get("calendar")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Calendar dataset not found at: {file_path}")

        logger.info(f"Extracting calendar dataset from: {file_path}")
        dtypes = {
            "wm_yr_wk": "int32",
            "weekday": "category",
            "wday": "int8",
            "month": "int8",
            "year": "int16",
            "d": "string",
            "event_name_1": "string",
            "event_type_1": "category",
            "event_name_2": "string",
            "event_type_2": "category",
            "snap_CA": "int8",
            "snap_TX": "int8",
            "snap_WI": "int8",
        }
        df = pd.read_csv(file_path, dtype=dtypes, parse_dates=["date"])
        logger.info(f"Loaded calendar dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df

    def extract_sell_prices(self, chunked: bool = False) -> Generator[pd.DataFrame, None, None] | pd.DataFrame:
        """Extracts sell_prices.csv (large dataset ~6.8M rows)."""
        file_path = self.data_paths.get("sell_prices")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Sell prices dataset not found at: {file_path}")

        logger.info(f"Extracting sell_prices dataset from: {file_path}")
        dtypes = {
            "store_id": "category",
            "item_id": "string",
            "wm_yr_wk": "int32",
            "sell_price": "float32"
        }

        if chunked:
            return pd.read_csv(file_path, dtype=dtypes, chunksize=self.chunk_size)
        else:
            df = pd.read_csv(file_path, dtype=dtypes)
            logger.info(f"Loaded sell_prices dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
            return df

    def extract_sales_validation(self) -> pd.DataFrame:
        """Extracts sales_train_validation.csv (30,490 rows x 1,919 columns)."""
        file_path = self.data_paths.get("sales_train_validation")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Sales validation dataset not found at: {file_path}")

        logger.info(f"Extracting sales_train_validation dataset from: {file_path}")
        # Optimize memory usage for 1913 daily count columns
        df = pd.read_csv(file_path)
        logger.info(f"Loaded sales_train_validation dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df

    def extract_sales_evaluation(self) -> pd.DataFrame:
        """Extracts sales_train_evaluation.csv if available."""
        file_path = self.data_paths.get("sales_train_evaluation")
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"Sales evaluation dataset not found at: {file_path}")
            return pd.DataFrame()

        logger.info(f"Extracting sales_train_evaluation dataset from: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded sales_train_evaluation dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df

    def extract_sample_submission(self) -> pd.DataFrame:
        """Extracts sample_submission.csv."""
        file_path = self.data_paths.get("sample_submission")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Sample submission dataset not found at: {file_path}")

        logger.info(f"Extracting sample_submission dataset from: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded sample_submission dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
