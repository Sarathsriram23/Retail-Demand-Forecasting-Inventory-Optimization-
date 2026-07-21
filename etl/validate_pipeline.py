import argparse
import sys
import yaml
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.logging_config import setup_logger
from src.db_adapter import DatabaseAdapter
from src.validators import M5DataValidator

logger = setup_logger(__name__)

def run_validation(config_path: str = "config/config.yaml", engine_override: str = None):
    """Runs standalone data validation audit on loaded database tables."""
    logger.info("Starting standalone M5 data quality validation audit...")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if engine_override:
        config["pipeline"]["default_engine"] = engine_override

    engine_type = config["pipeline"]["default_engine"]
    db_adapter = DatabaseAdapter(config, engine_type=engine_type)
    validator = M5DataValidator(db_adapter, config)

    report = validator.generate_quality_report()
    db_adapter.close()
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Standalone M5 Data Validation Audit")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config YAML file")
    parser.add_argument("--engine", type=str, choices=["duckdb", "bigquery"], help="Override default database engine")
    args = parser.parse_args()

    run_validation(config_path=args.config, engine_override=args.engine)
