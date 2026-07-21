import os
import pandas as pd
from typing import Dict, Any
from src.db_adapter import DatabaseAdapter
from config.logging_config import setup_logger

logger = setup_logger(__name__)

class M5DataLoader:
    """Manages table creation, schema initialization, and data loading into target storage."""

    def __init__(self, db_adapter: DatabaseAdapter, config: Dict[str, Any]):
        self.db = db_adapter
        self.config = config
        self.tables = config.get("tables", {})

    def initialize_schemas(self):
        """Executes DDL scripts for all M5 tables."""
        ddl_dir = "sql/ddl"
        ddl_files = sorted([f for f in os.listdir(ddl_dir) if f.endswith(".sql")])

        for ddl_file in ddl_files:
            file_path = os.path.join(ddl_dir, ddl_file)
            logger.info(f"Initializing schema from script: {file_path}")
            self.db.execute_script(file_path)

    def load_calendar(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads calendar dataframe into target table."""
        table_name = self.tables.get("calendar", "calendar")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)

    def load_sell_prices(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads sell_prices dataframe into target table."""
        table_name = self.tables.get("sell_prices", "sell_prices")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)

    def load_sales_train_validation(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads raw wide sales validation dataframe into target table."""
        table_name = self.tables.get("sales_train_validation", "sales_train_validation")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)

    def load_sales_train_evaluation(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads raw wide sales evaluation dataframe into target table."""
        table_name = self.tables.get("sales_train_evaluation", "sales_train_evaluation")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)

    def load_sample_submission(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads sample_submission dataframe into target table."""
        table_name = self.tables.get("sample_submission", "sample_submission")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)

    def load_sales_fact(self, df: pd.DataFrame, if_exists: str = "replace") -> int:
        """Loads normalized long format sales fact table."""
        table_name = self.tables.get("sales_fact", "sales_fact")
        return self.db.load_dataframe(df, table_name=table_name, if_exists=if_exists)
