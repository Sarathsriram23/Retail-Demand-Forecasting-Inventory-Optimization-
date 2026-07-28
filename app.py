import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("Retail Demand Forecasting Dashboard")
st.caption("Analyze sales trends and inventory performance")

# Load real dataset (TEMPORARY)
filtered_df = pd.read_csv("data/sales_train_validation.csv")


filtered_df = filtered_df.head(100)  # limit for performance

filtered_df["date"] = range(len(filtered_df))
filtered_df["sales"] = filtered_df.iloc[:, 6:].sum(axis=1)


# Select only day columns
day_cols = [col for col in filtered_df.columns if col.startswith("d_")]

filtered_df = filtered_df.melt(
    id_vars=["id"],
    value_vars=day_cols,   # IMPORTANT FIX
    var_name="day",
    value_name="value"
)


filtered_df["day"] = filtered_df["day"].str.replace("d_", "").astype(int)

filtered_df = filtered_df.head(1000) # pick one sales column

# Sidebar
st.sidebar.header("Filters")
store = st.sidebar.selectbox("Store", ["Store A", "Store B"])
category = st.sidebar.selectbox("Category", ["Electronics", "Clothing"])
date_range = st.sidebar.slider("Select number of days", 10, 50, 30)

# Apply filters
filtered_df = filtered_df.copy()

# Filter by number of days
filtered_df = filtered_df.tail(date_range)

# Handle empty data
if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()
filtered_df = filtered_df.tail(date_range)

# Metrics
st.markdown("---")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Sales", int(filtered_df["value"].sum()))
col2.metric("📊 Avg Sales", round(filtered_df["value"].mean(), 2))
col3.metric("🔥 Peak Sales", int(filtered_df["value"].max()))

st.markdown("### 📌 Insights")

if filtered_df["value"].mean() > 5:
    st.success("Sales are performing well 📈")
else:
    st.warning("Sales are low ⚠️ — improvement needed")

# Chart
st.markdown("---")

col1, col2 = st.columns(2)

# LEFT CHART
with col1:
    st.subheader("📈 Sales Trend")
    trend = filtered_df.groupby("day")["value"].sum().reset_index()
    st.line_chart(trend.set_index("day"))

# RIGHT CHART
with col2:
    st.subheader("📊 Sales Distribution")
    st.bar_chart(filtered_df["value"])
# Table
st.write("Blue = Actual Sales | Orange = Forecast Trend")
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df)

st.subheader("Sales Distribution")
st.subheader("📊 Sales Distribution")
st.bar_chart(filtered_df["value"])


st.subheader("📅 Last 10 Days Sales")

last_10 = filtered_df.sort_values(by="day").tail(10)
st.line_chart(last_10.set_index("day")["value"])

st.subheader("Sales Forecast (Moving Average)")

# Prepare time series
ts = filtered_df.groupby("day")["value"].sum().reset_index()

# Rolling average (7 days)
st.markdown("---")
st.subheader("📊 Sales Forecast vs Actual")

forecast_df = ts.copy()
forecast_df["forecast"] = forecast_df["value"].rolling(7).mean()

st.line_chart(forecast_df.set_index("day")[["value", "forecast"]])

# Plot actual vs forecast
st.line_chart(ts.set_index("day")[["value", "rolling_mean"]])

st.subheader("Next 7 Days Forecast")

last_value = ts["rolling_mean"].iloc[-1]

future_days = list(range(ts["day"].max() + 1, ts["day"].max() + 8))
future_values = [last_value] * 7

forecast_df = pd.DataFrame({
    "day": future_days,
    "forecast": future_values
})

st.line_chart(forecast_df.set_index("day"))

st.markdown("---")
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df)