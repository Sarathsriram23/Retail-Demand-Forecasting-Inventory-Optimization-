import pytest
import pandas as pd
from src.validators import M5DataValidator

@pytest.fixture
def sample_validator(mocker=None):
    config = {
        "tables": {"calendar": "calendar"},
        "validation": {}
    }
    class MockAdapter:
        def get_row_count(self, table_name):
            return 1969
    return M5DataValidator(MockAdapter(), config)

def test_validate_uniqueness(sample_validator):
    df = pd.DataFrame({"id": ["A", "B", "C"]})
    assert sample_validator.validate_uniqueness(df, key_cols=["id"], dataset_name="test") is True

    df_dups = pd.DataFrame({"id": ["A", "A", "B"]})
    assert sample_validator.validate_uniqueness(df_dups, key_cols=["id"], dataset_name="test") is False

def test_validate_missing_values(sample_validator):
    df = pd.DataFrame({"id": ["A", "B"], "val": [1, 2]})
    assert sample_validator.validate_missing_values(df, critical_cols=["id", "val"], dataset_name="test") is True

    df_nulls = pd.DataFrame({"id": ["A", None], "val": [1, 2]})
    assert sample_validator.validate_missing_values(df_nulls, critical_cols=["id"], dataset_name="test") is False

def test_validate_sell_prices_ranges(sample_validator):
    df = pd.DataFrame({"sell_price": [1.5, 9.99, 0.5]})
    assert sample_validator.validate_sell_prices_ranges(df) is True

    df_bad = pd.DataFrame({"sell_price": [1.5, -2.0, 0.0]})
    assert sample_validator.validate_sell_prices_ranges(df_bad) is False

def test_validate_schema(sample_validator):
    from src.schemas import SellPriceRow
    df = pd.DataFrame({
        "store_id": ["CA_1", "CA_2"],
        "item_id": ["HOBBIES_1", "HOBBIES_2"],
        "wm_yr_wk": [11101, 11102],
        "sell_price": [9.58, 8.26]
    })
    assert sample_validator.validate_schema(df, SellPriceRow, "sell_prices") is True

    # Bad data: negative sell price
    df_bad = pd.DataFrame({
        "store_id": ["CA_1"],
        "item_id": ["HOBBIES_1"],
        "wm_yr_wk": [11101],
        "sell_price": [-1.0]
    })
    assert sample_validator.validate_schema(df_bad, SellPriceRow, "sell_prices") is False

