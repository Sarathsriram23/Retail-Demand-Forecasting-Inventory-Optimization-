import pandas as pd

from src.dashboard import build_dashboard_payload, get_inventory_recommendations


def test_build_dashboard_payload_returns_expected_frames():
    payload = build_dashboard_payload(config={}, limit_rows=5)

    assert "historical_sales" in payload
    assert "forecast_view" in payload
    assert "recommendations" in payload

    historical_sales = payload["historical_sales"]
    forecast_view = payload["forecast_view"]
    recommendations = payload["recommendations"]

    assert isinstance(historical_sales, pd.DataFrame)
    assert isinstance(forecast_view, pd.DataFrame)
    assert isinstance(recommendations, pd.DataFrame)
    assert not historical_sales.empty
    assert not forecast_view.empty
    assert not recommendations.empty
    assert "date" in historical_sales.columns
    assert "store_id" in historical_sales.columns
    assert "forecast_qty" in forecast_view.columns


def test_get_inventory_recommendations_uses_price_change():
    recommendations = get_inventory_recommendations(
        pd.DataFrame(
            [{"store_id": "CA_1", "category_id": "FOODS", "sales_qty": 100, "current_stock": 80, "sell_price": 10.0}]
        ),
        price_change_pct=0.10,
    )

    assert not recommendations.empty
    assert recommendations.iloc[0]["recommended_qty"] >= 0
    assert recommendations.iloc[0]["action"] in {"Restock", "Hold"}
