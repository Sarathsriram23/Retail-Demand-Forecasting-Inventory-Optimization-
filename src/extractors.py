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

    def _resolve_data_path(self, file_path: Optional[str]) -> Optional[str]:
        """Resolve a dataset path relative to the repository root when needed."""
        if not file_path:
            return None

        path = Path(file_path)
        if path.is_absolute() or path.exists():
            return str(path)

        repo_root = Path(__file__).resolve().parents[1]
        candidate = repo_root / path
        if candidate.exists():
            return str(candidate)

        return str(path)

    def _fallback_calendar(self) -> pd.DataFrame:
        """Create a lightweight synthetic calendar dataset when the CSV is unavailable."""
        return pd.DataFrame(
            {
                "date": pd.date_range("2013-01-01", periods=5, freq="D"),
                "wm_yr_wk": [11301, 11302, 11303, 11304, 11305],
                "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "wday": [0, 1, 2, 3, 4],
                "month": [1, 1, 1, 1, 1],
                "year": [2013, 2013, 2013, 2013, 2013],
                "d": ["d_1", "d_2", "d_3", "d_4", "d_5"],
                "event_name_1": [None, None, None, None, None],
                "event_type_1": [None, None, None, None, None],
                "event_name_2": [None, None, None, None, None],
                "event_type_2": [None, None, None, None, None],
                "snap_CA": [0, 0, 0, 0, 0],
                "snap_TX": [0, 0, 0, 0, 0],
                "snap_WI": [0, 0, 0, 0, 0],
            }
        )

    def _fallback_sell_prices(self) -> pd.DataFrame:
        """Create a lightweight synthetic sell prices dataset when the CSV is unavailable."""
        return pd.DataFrame(
            {
                "store_id": ["CA_1", "CA_1", "CA_1", "CA_1", "CA_1"],
                "item_id": ["FOODS_1", "FOODS_1", "FOODS_2", "FOODS_2", "FOODS_3"],
                "wm_yr_wk": [11301, 11302, 11301, 11302, 11301],
                "sell_price": [3.97, 4.01, 2.99, 3.05, 1.99],
            }
        )

    def _fallback_sales_validation(self) -> pd.DataFrame:
        """Create a lightweight synthetic sales validation dataset when the CSV is unavailable."""
        return pd.DataFrame(
            {
                "id": ["FOODS_1_CA_1_1", "FOODS_2_CA_1_1", "FOODS_3_CA_1_1"],
                "item_id": ["FOODS_1", "FOODS_2", "FOODS_3"],
                "dept_id": [1, 1, 1],
                "cat_id": ["FOODS", "FOODS", "FOODS"],
                "store_id": ["CA_1", "CA_1", "CA_1"],
                "state_id": ["CA", "CA", "CA"],
                "d_1": [3, 2, 5],
                "d_2": [4, 2, 6],
            }
        )

    def extract_calendar(self) -> pd.DataFrame:
        """Extracts calendar.csv dimension table."""
        file_path = self._resolve_data_path(self.data_paths.get("calendar"))
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"Calendar dataset not found at: {file_path}. Using synthetic fallback data.")
            return self._fallback_calendar()

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
        file_path = self._resolve_data_path(self.data_paths.get("sell_prices"))
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"Sell prices dataset not found at: {file_path}. Using synthetic fallback data.")
            return self._fallback_sell_prices()

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
        file_path = self._resolve_data_path(self.data_paths.get("sales_train_validation"))
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"Sales validation dataset not found at: {file_path}. Using synthetic fallback data.")
            return self._fallback_sales_validation()

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
