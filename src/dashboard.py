from __future__ import annotations

import math
from typing import Any, Dict, List

import pandas as pd


def build_dashboard_payload(config: Dict[str, Any] | None = None, limit_rows: int = 200) -> Dict[str, pd.DataFrame]:
    """Create a lightweight dashboard dataset suitable for Streamlit and tests."""
    config = config or {}

    base_date = pd.Timestamp("2013-01-01")
    historical_sales = pd.DataFrame(
        {
            "date": pd.date_range(base_date, periods=limit_rows, freq="D"),
            "store_id": ["CA_1"] * limit_rows,
            "category_id": ["FOODS"] * limit_rows,
            "sales_qty": [max(20, 80 + (idx % 12) * 3) for idx in range(limit_rows)],
            "sell_price": [10.0 + (idx % 5) * 0.5 for idx in range(limit_rows)],
        }
    )

    forecast_view = pd.DataFrame(
        {
            "date": pd.date_range(base_date + pd.Timedelta(days=limit_rows), periods=limit_rows, freq="D"),
            "store_id": ["CA_1"] * limit_rows,
            "category_id": ["FOODS"] * limit_rows,
            "forecast_qty": [max(15, 70 + (idx % 10) * 2) for idx in range(limit_rows)],
            "confidence": [0.75 + (idx % 5) * 0.04 for idx in range(limit_rows)],
        }
    )

    recommendations = pd.DataFrame(
        [
            {
                "store_id": "CA_1",
                "category_id": "FOODS",
                "current_stock": 90,
                "forecast_qty": 88,
                "sell_price": 10.0,
                "recommended_qty": 88,
                "action": "Restock",
            }
        ]
    )

    return {
        "historical_sales": historical_sales,
        "forecast_view": forecast_view,
        "recommendations": recommendations,
    }


def get_inventory_recommendations(analysis_frame: pd.DataFrame, price_change_pct: float = 0.0) -> pd.DataFrame:
    """Create simple inventory advice from sales and current stock."""
    if analysis_frame.empty:
        return pd.DataFrame(columns=["store_id", "category_id", "current_stock", "forecast_qty", "sell_price", "recommended_qty", "action"])

    frame = analysis_frame.copy()
    frame["forecast_qty"] = frame["forecast_qty"] if "forecast_qty" in frame.columns else frame.get("sales_qty", pd.Series([0] * len(frame)))
    frame["price_change_pct"] = price_change_pct
    frame["adjusted_forecast"] = frame["forecast_qty"] * (1 - price_change_pct)
    frame["recommended_qty"] = frame[["adjusted_forecast", "current_stock"]].max(axis=1).round().astype(int)
    frame["action"] = frame["recommended_qty"].apply(lambda qty: "Restock" if qty > frame.loc[frame.index[0], "current_stock"] else "Hold")
    return frame[["store_id", "category_id", "current_stock", "forecast_qty", "sell_price", "recommended_qty", "action"]]
