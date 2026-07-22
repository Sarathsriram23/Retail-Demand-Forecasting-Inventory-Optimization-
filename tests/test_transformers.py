import pytest
import pandas as pd
from src.transformers import M5DataTransformer

@pytest.fixture
def sample_config():
    return {}

def test_deduplicate(sample_config):
    transformer = M5DataTransformer(sample_config)
    data = {
        "store_id": ["CA_1", "CA_1", "TX_1"],
        "item_id": ["HOBBIES_1", "HOBBIES_1", "HOBBIES_1"],
        "wm_yr_wk": [11101, 11101, 11101],
        "sell_price": [9.58, 9.58, 8.26]
    }
    df = pd.DataFrame(data)
    clean_df = transformer.deduplicate(df, key_columns=["store_id", "item_id", "wm_yr_wk"], dataset_name="test")
    assert len(clean_df) == 2

def test_handle_calendar_missing_values(sample_config):
    transformer = M5DataTransformer(sample_config)
    data = {
        "date": ["2011-01-29", "2011-01-30"],
        "wm_yr_wk": [11101, 11101],
        "weekday": ["Saturday", "Sunday"],
        "wday": [1, 2],
        "month": [1, 1],
        "year": [2011, 2011],
        "d": ["d_1", "d_2"],
        "event_name_1": [None, "SuperBowl"],
        "snap_CA": [0, 0],
        "snap_TX": [0, 0],
        "snap_WI": [0, 0]
    }
    df = pd.DataFrame(data)
    clean_df = transformer.handle_calendar_missing_values(df)
    assert clean_df["event_name_1"].iloc[0] == "None"
    assert clean_df["event_name_1"].iloc[1] == "SuperBowl"

def test_transform_sales_wide_to_long(sample_config):
    transformer = M5DataTransformer(sample_config)
    sales_data = {
        "id": ["HOBBIES_1_001_CA_1_validation"],
        "item_id": ["HOBBIES_1_001"],
        "dept_id": ["HOBBIES_1"],
        "cat_id": ["HOBBIES"],
        "store_id": ["CA_1"],
        "state_id": ["CA"],
        "d_1": [3],
        "d_2": [5]
    }
    cal_data = {
        "d": ["d_1", "d_2"],
        "date": ["2011-01-29", "2011-01-30"]
    }
    sales_df = pd.DataFrame(sales_data)
    cal_df = pd.DataFrame(cal_data)
    
    chunks = list(transformer.transform_sales_wide_to_long_chunks(sales_df, cal_df, chunk_size=1))
    assert len(chunks) == 1
    long_df = chunks[0]
    assert len(long_df) == 2
    assert "sales_qty" in long_df.columns
    assert "date" in long_df.columns
    assert list(long_df["sales_qty"]) == [3, 5]

