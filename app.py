import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("Retail Demand Dashboard")

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

# Metrics
col1, col2 = st.columns(2)

col1.metric("Avg Sales", int(df["sales"].mean()))
col2.metric("Max Sales", int(df["sales"].max()))

# Chart
st.subheader("Sales Trend")
st.line_chart(df.set_index("date"))

# Table
st.subheader("Data")
st.dataframe(df)