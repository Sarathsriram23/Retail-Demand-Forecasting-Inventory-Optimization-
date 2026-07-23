import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("Retail Demand Forecasting Dashboard")
st.caption("Analyze sales trends and inventory performance")

# Dummy data
dates = pd.date_range(start="2024-01-01", periods=50)
sales = np.random.randint(10, 100, size=50)

df = pd.DataFrame({
    "date": dates,
    "sales": sales
})

# Sidebar
st.sidebar.header("Filters")
store = st.sidebar.selectbox("Store", ["Store A", "Store B"])
category = st.sidebar.selectbox("Category", ["Electronics", "Clothing"])
date_range = st.sidebar.slider("Select number of days", 10, 50, 30)

filtered_df = df.tail(date_range)

# Metrics
col1, col2, col3 = st.columns(3)

col1.metric("Avg Sales", int(df["sales"].mean()))
col2.metric("Max Sales", int(df["sales"].max()))
col3.metric("Min Sales", int(df["sales"].min()))
# Chart
st.subheader("Sales Trend")
st.line_chart(df.set_index("date"))

# Table
st.subheader("Data")
st.dataframe(df)

st.markdown("---")

st.subheader("Sales Distribution")
st.bar_chart(filtered_df["sales"])

st.subheader("Last 10 Days Sales")
st.line_chart(filtered_df.tail(10).set_index("date"))