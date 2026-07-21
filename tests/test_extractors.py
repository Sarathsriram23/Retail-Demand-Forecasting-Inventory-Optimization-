import pytest
import pandas as pd
from src.extractors import M5DataExtractor

@pytest.fixture
def sample_config():
    return {
        "data_paths": {
            "calendar": "m5-forecasting-accuracy/calendar.csv",
            "sales_train_validation": "m5-forecasting-accuracy/sales_train_validation.csv",
            "sell_prices": "m5-forecasting-accuracy/sell_prices.csv",
            "sample_submission": "m5-forecasting-accuracy/sample_submission.csv"
        },
        "pipeline": {"chunk_size": 1000}
    }

def test_extract_calendar(sample_config):
    extractor = M5DataExtractor(sample_config)
    df = extractor.extract_calendar()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "date" in df.columns
    assert "wm_yr_wk" in df.columns
    assert "d" in df.columns

def test_extract_sell_prices(sample_config):
    extractor = M5DataExtractor(sample_config)
    df = extractor.extract_sell_prices(chunked=False)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "store_id" in df.columns
    assert "item_id" in df.columns
    assert "sell_price" in df.columns

def test_extract_sales_validation(sample_config):
    extractor = M5DataExtractor(sample_config)
    df = extractor.extract_sales_validation()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "id" in df.columns
    assert "d_1" in df.columns
