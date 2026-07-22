from __future__ import annotations

import pandas as pd
import streamlit as st

from src.dashboard import build_dashboard_payload, get_inventory_recommendations

st.set_page_config(page_title="Retail Demand Dashboard", page_icon="📈", layout="wide")

st.title("Retail Demand Forecasting & Inventory Dashboard")
st.caption("Interactive storefront view for historical demand, forecasts, and pricing what-if scenarios.")

payload = build_dashboard_payload(limit_rows=120)
historical_sales = payload["historical_sales"]
forecast_view = payload["forecast_view"]
base_recommendations = payload["recommendations"]

with st.sidebar:
    st.header("Filters")
    store_ids = sorted(historical_sales["store_id"].unique().tolist())
    selected_store = st.selectbox("Store", store_ids)
    category_ids = sorted(historical_sales["category_id"].unique().tolist())
    selected_category = st.selectbox("Category", category_ids)
    price_drop = st.slider("Price drop simulation (%)", 0, 25, 10, 1) / 100

filtered_sales = historical_sales[
    (historical_sales["store_id"] == selected_store) & (historical_sales["category_id"] == selected_category)
].copy()
filtered_forecast = forecast_view[
    (forecast_view["store_id"] == selected_store) & (forecast_view["category_id"] == selected_category)
].copy()

analysis_frame = pd.DataFrame(
    [
        {
            "store_id": selected_store,
            "category_id": selected_category,
            "current_stock": int(base_recommendations.iloc[0]["current_stock"]),
            "forecast_qty": int(filtered_forecast["forecast_qty"].mean()),
            "sell_price": float(filtered_sales["sell_price"].mean()),
        }
    ]
)
recommendations = get_inventory_recommendations(analysis_frame, price_change_pct=price_drop)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Selected store", selected_store)
with col2:
    st.metric("Avg. daily sales", round(float(filtered_sales["sales_qty"].mean()), 1))
with col3:
    st.metric("Forecasted demand", round(float(filtered_forecast["forecast_qty"].mean()), 1))

st.subheader("Historical sales")
st.line_chart(filtered_sales.set_index("date")["sales_qty"])

st.subheader("Forecast comparison")
comparison = pd.DataFrame(
    {
        "Historical": filtered_sales.set_index("date")["sales_qty"].tail(30).reset_index(drop=True),
        "Forecast": filtered_forecast["forecast_qty"].tail(30).reset_index(drop=True),
    }
)
st.bar_chart(comparison)

st.subheader("What-if analysis")
st.dataframe(recommendations, use_container_width=True)

st.subheader("Forecast table")
st.dataframe(filtered_forecast.head(20), use_container_width=True)
