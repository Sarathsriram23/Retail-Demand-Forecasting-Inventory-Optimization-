import os
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from config.logging_config import setup_logger

logger = setup_logger(__name__)

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False
    duckdb = None

class DatabaseAdapter:
    """Unified Database Abstraction supporting both Google BigQuery and DuckDB local engine."""

    def __init__(self, config: Dict[str, Any], engine_type: Optional[str] = None):
        self.config = config
        self.engine_type = engine_type or config.get("pipeline", {}).get("default_engine", "duckdb")
        self.bq_client = None
        self.duck_conn = None

        if self.engine_type.lower() == "bigquery":
            self._init_bigquery()
        else:
            self._init_duckdb()

    def _init_bigquery(self):
        """Initializes Google BigQuery Client."""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account

            cred_path = self.config.get("bigquery", {}).get("credentials_file")
            project_id = self.config.get("bigquery", {}).get("project_id")

            if cred_path and os.path.exists(cred_path):
                credentials = service_account.Credentials.from_service_account_file(cred_path)
                self.bq_client = bigquery.Client(project=project_id, credentials=credentials)
                logger.info(f"Initialized BigQuery client with service account: {cred_path}")
            else:
                # Default Application Credentials or ambient environment
                self.bq_client = bigquery.Client(project=project_id)
                logger.info("Initialized BigQuery client with environment credentials.")

            self.dataset_id = self.config.get("bigquery", {}).get("dataset_id", "m5_retail_demand")
            self._ensure_bq_dataset()
        except Exception as e:
            logger.warning(f"Failed to initialize BigQuery client ({e}). Falling back to DuckDB engine.")
            self.engine_type = "duckdb"
            self._init_duckdb()

    def _ensure_bq_dataset(self):
        """Creates dataset if not exists in BigQuery."""
        from google.cloud import bigquery
        dataset_ref = f"{self.bq_client.project}.{self.dataset_id}"
        location = self.config.get("bigquery", {}).get("location", "US")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        try:
            self.bq_client.create_dataset(dataset, exists_ok=True)
            logger.info(f"BigQuery dataset verified/created: {dataset_ref}")
        except Exception as e:
            logger.error(f"Error creating dataset {dataset_ref}: {e}")

    def _init_duckdb(self):
        """Initializes DuckDB or SQLite connection for local execution."""
        if HAS_DUCKDB:
            db_path = self.config.get("duckdb", {}).get("db_path", "data/m5_local.duckdb")
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.duck_conn = duckdb.connect(db_path)
            logger.info(f"Initialized DuckDB local connection at: {db_path}")
        else:
            db_path = "data/m5_local.db"
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.sqlite_conn = sqlite3.connect(db_path)
            logger.info(f"Initialized SQLite fallback connection at: {db_path}")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes SQL query and returns result as DataFrame."""
        if self.engine_type == "bigquery":
            query_job = self.bq_client.query(query)
            return query_job.to_dataframe()
        elif HAS_DUCKDB:
            return self.duck_conn.execute(query).df()
        else:
            return pd.read_sql_query(query, self.sqlite_conn)

    def execute_script(self, script_path: str):
        """Executes a SQL DDL/DML script from file path."""
        with open(script_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Remove single-line comments starting with --
        clean_sqls = [
            statement.strip() 
            for statement in sql_content.split(";") 
            if statement.strip() and not statement.strip().startswith("--")
        ]

        for sql in clean_sqls:
            if not sql:
                continue
            if self.engine_type == "bigquery":
                logger.info(f"Executing BigQuery statement: {sql[:60]}...")
                self.bq_client.query(sql).result()
            elif HAS_DUCKDB:
                logger.info(f"Executing DuckDB statement: {sql[:60]}...")
                self.duck_conn.execute(sql)
            else:
                logger.info(f"Executing SQLite statement: {sql[:60]}...")
                # Strip BigQuery specific data types if using SQLite fallback
                sql_sqlite = sql.replace("INT64", "INTEGER").replace("STRING", "TEXT").replace("NUMERIC", "REAL").replace("DATE", "TEXT")
                self.sqlite_conn.cursor().executescript(sql_sqlite)
                self.sqlite_conn.commit()

    def load_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "append") -> int:
        """Loads a pandas DataFrame into target table."""
        if df.empty:
            logger.warning(f"DataFrame for table '{table_name}' is empty. Skipping load.")
            return 0

        rows = len(df)
        if self.engine_type == "bigquery":
            from google.cloud import bigquery
            table_ref = f"{self.bq_client.project}.{self.dataset_id}.{table_name}"
            write_disposition = (
                bigquery.WriteDisposition.WRITE_TRUNCATE
                if if_exists == "replace"
                else bigquery.WriteDisposition.WRITE_APPEND
            )
            job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
            job = self.bq_client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()  # Wait for completion
            logger.info(f"Successfully loaded {rows} rows into BigQuery table '{table_ref}'")
        elif HAS_DUCKDB:
            if if_exists == "replace":
                self.duck_conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.duck_conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
            else:
                tbl_exists = self.duck_conn.execute(
                    f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name='{table_name}'"
                ).fetchone()[0] > 0

                if not tbl_exists:
                    self.duck_conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
                else:
                    self.duck_conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
            logger.info(f"Successfully loaded {rows} rows into DuckDB table '{table_name}'")
        else:
            df.to_sql(table_name, self.sqlite_conn, if_exists=if_exists, index=False)
            logger.info(f"Successfully loaded {rows} rows into SQLite table '{table_name}'")

        return rows

    def get_row_count(self, table_name: str) -> int:
        """Returns total row count for table."""
        query = f"SELECT COUNT(*) as cnt FROM {self.dataset_id + '.' + table_name if self.engine_type == 'bigquery' else table_name}"
        res = self.execute_query(query)
        return int(res.iloc[0]["cnt"])

    def close(self):
        """Closes connections."""
        if HAS_DUCKDB and getattr(self, 'duck_conn', None):
            self.duck_conn.close()
            logger.info("DuckDB connection closed.")
        elif getattr(self, 'sqlite_conn', None):
            self.sqlite_conn.close()
            logger.info("SQLite connection closed.")

