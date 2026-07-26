import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Retail Dashboard", layout="wide")

st.title("Retail Demand Forecasting Dashboard")
st.caption("Analyze sales trends and inventory performance")

# Load real dataset (TEMPORARY)
df = pd.read_csv("data/sales_train_validation.csv")


df = df.head(100)  # limit for performance

df["date"] = range(len(df))
df["sales"] = df.iloc[:, 6:].sum(axis=1)


# ✅ Select only day columns
day_cols = [col for col in df.columns if col.startswith("d_")]

df_long = df.melt(
    id_vars=["id"],
    value_vars=day_cols,   # 🔥 IMPORTANT FIX
    var_name="day",
    value_name="value"
)


df_long["day"] = df_long["day"].str.replace("d_", "").astype(int)

df_long = df_long.head(1000) # pick one sales column

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
st.line_chart(df_long.groupby("day")["value"].sum())

# Table
st.subheader("Data")
st.dataframe(df)

st.markdown("---")

st.subheader("Sales Distribution")
st.bar_chart(filtered_df["sales"])

st.subheader("Last 10 Days Sales")
last_10 = df_long.groupby("day")["value"].sum().tail(10)
st.line_chart(last_10)