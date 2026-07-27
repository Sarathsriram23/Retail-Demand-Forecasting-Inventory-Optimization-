import os
import sys
import logging
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for visualizations
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16,
    "figure.dpi": 300
})

DATA_DIR = os.path.join(os.getcwd(), "m5-forecasting-accuracy")
CLEANED_DIR = os.path.join(os.getcwd(), "data", "cleaned")
CHARTS_DIR = os.path.join(os.getcwd(), "reports", "charts")

os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("m5_eda_cleaning")

def main():
    logger.info("=== Starting M5 Forecasting Data Cleaning & EDA Pipeline ===")

    # 1. Load CSV Files & Initial Audit using DuckDB
    conn = duckdb.connect()
    conn.execute("SET max_expression_depth = 5000;")

    calendar_path = os.path.join(DATA_DIR, "calendar.csv").replace("\\", "/")
    prices_path = os.path.join(DATA_DIR, "sell_prices.csv").replace("\\", "/")
    val_path = os.path.join(DATA_DIR, "sales_train_validation.csv").replace("\\", "/")
    eval_path = os.path.join(DATA_DIR, "sales_train_evaluation.csv").replace("\\", "/")
    sub_path = os.path.join(DATA_DIR, "sample_submission.csv").replace("\\", "/")

    logger.info("Task 1: Loading raw CSV datasets into DuckDB...")
    conn.execute(f"CREATE TABLE raw_calendar AS SELECT * FROM read_csv_auto('{calendar_path}')")
    conn.execute(f"CREATE TABLE raw_sell_prices AS SELECT * FROM read_csv_auto('{prices_path}')")
    conn.execute(f"CREATE TABLE raw_sales_eval AS SELECT * FROM read_csv_auto('{eval_path}')")
    conn.execute(f"CREATE TABLE raw_sales_val AS SELECT * FROM read_csv_auto('{val_path}')")
    conn.execute(f"CREATE TABLE raw_sample_sub AS SELECT * FROM read_csv_auto('{sub_path}')")

    cal_count = conn.execute("SELECT COUNT(*) FROM raw_calendar").fetchone()[0]
    prices_count = conn.execute("SELECT COUNT(*) FROM raw_sell_prices").fetchone()[0]
    eval_count = conn.execute("SELECT COUNT(*) FROM raw_sales_eval").fetchone()[0]
    val_count = conn.execute("SELECT COUNT(*) FROM raw_sales_val").fetchone()[0]
    sub_count = conn.execute("SELECT COUNT(*) FROM raw_sample_sub").fetchone()[0]

    logger.info(f"Loaded Raw Row Counts:")
    logger.info(f" - Calendar: {cal_count:,} rows")
    logger.info(f" - Sell Prices: {prices_count:,} rows")
    logger.info(f" - Sales Evaluation: {eval_count:,} rows")
    logger.info(f" - Sales Validation: {val_count:,} rows")
    logger.info(f" - Sample Submission: {sub_count:,} rows")

    # 2. Handle Missing Values
    logger.info("Task 2: Auditing and handling missing values...")
    conn.execute("""
        CREATE TABLE calendar_clean AS
        SELECT
            CAST(date AS DATE) AS date,
            CAST(wm_yr_wk AS INT) AS wm_yr_wk,
            weekday,
            CAST(wday AS INT) AS wday,
            CAST(month AS INT) AS month,
            CAST(year AS INT) AS year,
            d,
            COALESCE(event_name_1, 'None') AS event_name_1,
            COALESCE(event_type_1, 'None') AS event_type_1,
            COALESCE(event_name_2, 'None') AS event_name_2,
            COALESCE(event_type_2, 'None') AS event_type_2,
            CAST(snap_CA AS INT) AS snap_CA,
            CAST(snap_TX AS INT) AS snap_TX,
            CAST(snap_WI AS INT) AS snap_WI
        FROM raw_calendar
    """)

    null_prices = conn.execute("SELECT COUNT(*) FROM raw_sell_prices WHERE sell_price IS NULL OR store_id IS NULL OR item_id IS NULL OR wm_yr_wk IS NULL").fetchone()[0]
    logger.info(f"Null count in sell_prices: {null_prices}")
    conn.execute("""
        CREATE TABLE sell_prices_clean AS
        SELECT
            store_id,
            item_id,
            CAST(wm_yr_wk AS INT) AS wm_yr_wk,
            CAST(sell_price AS DOUBLE) AS sell_price
        FROM raw_sell_prices
        WHERE sell_price IS NOT NULL
    """)

    conn.execute("CREATE TABLE sales_eval_clean AS SELECT * FROM raw_sales_eval")

    # 3. Duplicate Checks & Removal
    logger.info("Task 3: Checking and removing duplicate records...")
    cal_dup = conn.execute("SELECT COUNT(*) - COUNT(DISTINCT d) FROM calendar_clean").fetchone()[0]
    prices_dup = conn.execute("SELECT COUNT(*) - COUNT(DISTINCT store_id || '_' || item_id || '_' || CAST(wm_yr_wk AS VARCHAR)) FROM sell_prices_clean").fetchone()[0]
    sales_dup = conn.execute("SELECT COUNT(*) - COUNT(DISTINCT id) FROM sales_eval_clean").fetchone()[0]

    logger.info(f"Duplicate counts on primary keys:")
    logger.info(f" - Calendar duplicates (key='d'): {cal_dup}")
    logger.info(f" - Sell Prices duplicates (key='store_id, item_id, wm_yr_wk'): {prices_dup}")
    logger.info(f" - Sales Evaluation duplicates (key='id'): {sales_dup}")

    # 4. Date Conversions & Data Consistency Checks
    logger.info("Task 4 & 5: Date conversions & consistency validation...")

    invalid_prices = conn.execute("SELECT COUNT(*) FROM sell_prices_clean WHERE sell_price <= 0").fetchone()[0]
    logger.info(f"Invalid prices (price <= 0): {invalid_prices}")

    stores = conn.execute("SELECT DISTINCT store_id FROM sales_eval_clean ORDER BY store_id").fetchall()
    categories = conn.execute("SELECT DISTINCT cat_id FROM sales_eval_clean ORDER BY cat_id").fetchall()
    departments = conn.execute("SELECT DISTINCT dept_id FROM sales_eval_clean ORDER BY dept_id").fetchall()
    states = conn.execute("SELECT DISTINCT state_id FROM sales_eval_clean ORDER BY state_id").fetchall()

    logger.info(f"Distinct Stores ({len(stores)}): {[s[0] for s in stores]}")
    logger.info(f"Distinct Categories ({len(categories)}): {[c[0] for c in categories]}")
    logger.info(f"Distinct Departments ({len(departments)}): {[d[0] for d in departments]}")
    logger.info(f"Distinct States ({len(states)}): {[s[0] for s in states]}")

    # 5. Export Clean Datasets to Parquet & CSV
    logger.info("Exporting cleaned tables to data/cleaned/ ...")

    cal_df = conn.execute("SELECT * FROM calendar_clean").df()
    cal_df.to_parquet(os.path.join(CLEANED_DIR, "calendar_clean.parquet"), index=False)
    cal_df.to_csv(os.path.join(CLEANED_DIR, "calendar_clean.csv"), index=False)

    prices_df = conn.execute("SELECT * FROM sell_prices_clean").df()
    prices_df.to_parquet(os.path.join(CLEANED_DIR, "sell_prices_clean.parquet"), index=False)
    prices_df.to_csv(os.path.join(CLEANED_DIR, "sell_prices_clean.csv"), index=False)

    sales_eval_df = conn.execute("SELECT * FROM sales_eval_clean").df()
    sales_eval_df.to_parquet(os.path.join(CLEANED_DIR, "sales_train_evaluation_clean.parquet"), index=False)
    sales_eval_df.to_csv(os.path.join(CLEANED_DIR, "sales_train_evaluation_clean.csv"), index=False)

    logger.info("Clean datasets exported successfully.")

    # 6. Generate Descriptive Statistics & Analytics
    logger.info("Task 6: Computing descriptive statistics and aggregations...")

    price_stats = conn.execute("""
        SELECT
            cat_id,
            COUNT(*) as count,
            AVG(sell_price) as mean_price,
            STDDEV(sell_price) as std_price,
            MIN(sell_price) as min_price,
            MEDIAN(sell_price) as median_price,
            MAX(sell_price) as max_price
        FROM sell_prices_clean p
        JOIN (SELECT DISTINCT item_id, cat_id FROM sales_eval_clean) s ON p.item_id = s.item_id
        GROUP BY cat_id
        ORDER BY mean_price DESC
    """).df()

    logger.info("\n=== Sell Price Statistics by Category ===")
    logger.info(f"\n{price_stats.to_string(index=False)}")

    logger.info("Unpivoting daily sales time series for store and category aggregations...")

    store_sales_df = conn.execute("""
        WITH melted AS (
            UNPIVOT sales_eval_clean
            ON COLUMNS(* EXCLUDE (id, item_id, dept_id, cat_id, store_id, state_id))
            INTO
                NAME d
                VALUE sales_qty
        )
        SELECT
            store_id,
            state_id,
            COUNT(DISTINCT id) as item_count,
            SUM(sales_qty) as total_units_sold
        FROM melted
        GROUP BY store_id, state_id
        ORDER BY total_units_sold DESC
    """).df()

    logger.info("\n=== Sales Volume by Store ===")
    logger.info(f"\n{store_sales_df.to_string(index=False)}")

    cat_sales_df = conn.execute("""
        WITH melted AS (
            UNPIVOT sales_eval_clean
            ON COLUMNS(* EXCLUDE (id, item_id, dept_id, cat_id, store_id, state_id))
            INTO
                NAME d
                VALUE sales_qty
        )
        SELECT
            cat_id,
            COUNT(DISTINCT id) as item_count,
            SUM(sales_qty) as total_units_sold
        FROM melted
        GROUP BY cat_id
        ORDER BY total_units_sold DESC
    """).df()

    logger.info("\n=== Sales Volume by Category ===")
    logger.info(f"\n{cat_sales_df.to_string(index=False)}")

    logger.info("Unpivoting daily sales time series for temporal analysis...")

    daily_sales_ts = conn.execute("""
        WITH melted AS (
            UNPIVOT sales_eval_clean
            ON COLUMNS(* EXCLUDE (id, item_id, dept_id, cat_id, store_id, state_id))
            INTO
                NAME d
                VALUE sales_qty
        )
        SELECT
            c.date,
            c.wm_yr_wk,
            c.weekday,
            c.wday,
            c.month,
            c.year,
            c.event_name_1,
            c.event_type_1,
            c.snap_CA,
            c.snap_TX,
            c.snap_WI,
            m.state_id,
            m.store_id,
            m.cat_id,
            SUM(m.sales_qty) as total_sales,
            AVG(m.sales_qty) as avg_sales_per_item,
            COUNT(CASE WHEN m.sales_qty = 0 THEN 1 END) * 100.0 / COUNT(*) as zero_sales_pct
        FROM melted m
        JOIN calendar_clean c ON m.d = c.d
        GROUP BY
            c.date, c.wm_yr_wk, c.weekday, c.wday, c.month, c.year,
            c.event_name_1, c.event_type_1, c.snap_CA, c.snap_TX, c.snap_WI,
            m.state_id, m.store_id, m.cat_id
    """).df()

    total_daily = daily_sales_ts.groupby("date")["total_sales"].sum().reset_index()
    total_daily["date"] = pd.to_datetime(total_daily["date"])
    total_daily = total_daily.sort_values("date")
    total_daily["rolling_28d"] = total_daily["total_sales"].rolling(window=28).mean()

    # 7. Generate Visualizations (Task 7)
    logger.info("Task 7: Rendering and saving high-resolution visual charts...")

    # Chart 1: Total Sales Over Time
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(total_daily["date"], total_daily["total_sales"], alpha=0.35, color="#2b5c8f", label="Daily Total Sales")
    ax.plot(total_daily["date"], total_daily["rolling_28d"], color="#d95f02", linewidth=2.5, label="28-Day Moving Average")
    ax.set_title("M5 Dataset: Total Daily Unit Sales (2011 - 2016)", pad=15)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Units Sold")
    ax.legend(loc="upper left")
    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "total_sales_over_time.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 1: {chart1_path}")

    # Chart 2: Sales by Category and State
    cat_state_sales = daily_sales_ts.groupby(["cat_id", "state_id"])["total_sales"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=cat_state_sales, x="cat_id", y="total_sales", hue="state_id", palette="Blues_d", ax=ax)
    ax.set_title("Total Sales Volume by Category & State", pad=15)
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Total Units Sold (Millions)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}M".format(int(x/1e6))))
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f"{p.get_height()/1e6:.1f}M",
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                        textcoords='offset points')
    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "sales_by_category_state.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 2: {chart2_path}")

    # Chart 3: Price Distribution by Category
    prices_with_cat = conn.execute("""
        SELECT p.sell_price, s.cat_id, s.dept_id
        FROM sell_prices_clean p
        JOIN (SELECT DISTINCT item_id, cat_id, dept_id FROM sales_eval_clean) s ON p.item_id = s.item_id
    """).df()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=prices_with_cat, x="cat_id", y="sell_price", palette="Set2", ax=ax, showfliers=False)
    ax.set_title("Sell Price Distribution by Product Category (Excl. Outliers)", pad=15)
    ax.set_xlabel("Product Category")
    ax.set_ylabel("Sell Price ($)")
    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "price_distribution_by_category.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 3: {chart3_path}")

    # Chart 4: SNAP Impact Analysis
    snap_ca = daily_sales_ts[daily_sales_ts["state_id"] == "CA"].groupby("snap_CA")["total_sales"].mean().reset_index().rename(columns={"snap_CA": "snap", "total_sales": "CA"})
    snap_tx = daily_sales_ts[daily_sales_ts["state_id"] == "TX"].groupby("snap_TX")["total_sales"].mean().reset_index().rename(columns={"snap_TX": "snap", "total_sales": "TX"})
    snap_wi = daily_sales_ts[daily_sales_ts["state_id"] == "WI"].groupby("snap_WI")["total_sales"].mean().reset_index().rename(columns={"snap_WI": "snap", "total_sales": "WI"})
    snap_df = snap_ca.merge(snap_tx, on="snap").merge(snap_wi, on="snap")
    snap_df["snap_label"] = snap_df["snap"].map({0: "Non-SNAP Days", 1: "SNAP Purchase Days"})
    snap_melted = snap_df.melt(id_vars=["snap_label"], value_vars=["CA", "TX", "WI"], var_name="State", value_name="Avg_Daily_Sales")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=snap_melted, x="State", y="Avg_Daily_Sales", hue="snap_label", palette="crest", ax=ax)
    ax.set_title("Impact of SNAP Days on Average Store Sales Volume", pad=15)
    ax.set_xlabel("State")
    ax.set_ylabel("Average Store Daily Units Sold")
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f"{p.get_height():,.0f}",
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=9, xytext=(0, 3),
                        textcoords='offset points')
    plt.tight_layout()
    chart4_path = os.path.join(CHARTS_DIR, "snap_impact_analysis.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 4: {chart4_path}")

    # Chart 5: Event / Holiday Sales Impact
    event_sales = daily_sales_ts[daily_sales_ts["event_name_1"] != "None"].groupby("event_name_1")["total_sales"].mean().reset_index()
    baseline_sales = daily_sales_ts[daily_sales_ts["event_name_1"] == "None"]["total_sales"].mean()
    event_sales["pct_diff"] = ((event_sales["total_sales"] - baseline_sales) / baseline_sales) * 100
    top_bottom_events = pd.concat([event_sales.sort_values("pct_diff", ascending=False).head(8),
                                    event_sales.sort_values("pct_diff", ascending=True).head(8)]).drop_duplicates()

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#2ca02c" if x >= 0 else "#d62728" for x in top_bottom_events["pct_diff"]]
    sns.barplot(data=top_bottom_events, y="event_name_1", x="pct_diff", palette=colors, ax=ax)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_title("Sales Volume % Impact of Key Calendar Events vs. Non-Event Days", pad=15)
    ax.set_xlabel("% Change in Daily Average Sales")
    ax.set_ylabel("Calendar Event / Holiday")
    plt.tight_layout()
    chart5_path = os.path.join(CHARTS_DIR, "event_sales_impact.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 5: {chart5_path}")

    # Chart 6: Top 10 vs Bottom 10 Selling Items
    item_totals = conn.execute("""
        WITH melted AS (
            UNPIVOT sales_eval_clean
            ON COLUMNS(* EXCLUDE (id, item_id, dept_id, cat_id, store_id, state_id))
            INTO
                NAME d
                VALUE sales_qty
        )
        SELECT
            item_id,
            cat_id,
            SUM(sales_qty) as total_units
        FROM melted
        GROUP BY item_id, cat_id
        ORDER BY total_units DESC
    """).df()

    top_10 = item_totals.head(10).copy()
    top_10["group"] = "Top 10 Selling Items"
    bottom_10 = item_totals.tail(10).copy()
    bottom_10["group"] = "Bottom 10 Selling Items"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    sns.barplot(data=top_10, y="item_id", x="total_units", palette="viridis", ax=ax1)
    ax1.set_title("Top 10 Best Selling Items (Cumulative Units)")
    ax1.set_xlabel("Total Units Sold")
    ax1.set_ylabel("Item ID")

    sns.barplot(data=bottom_10, y="item_id", x="total_units", palette="magma", ax=ax2)
    ax2.set_title("Bottom 10 Lowest Selling Items (Cumulative Units)")
    ax2.set_xlabel("Total Units Sold")
    ax2.set_ylabel("Item ID")
    plt.tight_layout()
    chart6_path = os.path.join(CHARTS_DIR, "top_bottom_selling_items.png")
    plt.savefig(chart6_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 6: {chart6_path}")

    # Chart 7: Weekly Seasonality Heatmap
    heatmap_data = daily_sales_ts.groupby(["weekday", "month"])["total_sales"].mean().reset_index()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot_heat = heatmap_data.pivot(index="weekday", columns="month", values="total_sales").reindex(day_order)
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot_heat.columns = month_names

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot_heat, annot=True, fmt=",.0f", cmap="YlGnBu", ax=ax, cbar_kws={'label': 'Avg Daily Units Sold'})
    ax.set_title("Seasonality Heatmap: Average Daily Sales Volume by Day of Week vs. Month", pad=15)
    ax.set_xlabel("Month")
    ax.set_ylabel("Day of Week")
    plt.tight_layout()
    chart7_path = os.path.join(CHARTS_DIR, "weekly_seasonality_heatmap.png")
    plt.savefig(chart7_path, dpi=300)
    plt.close()
    logger.info(f"Saved Chart 7: {chart7_path}")

    # Save summary statistics to JSON
    summary_file = os.path.join(CLEANED_DIR, "summary_stats.json")
    stats_dict = {
        "cal_count": int(cal_count),
        "prices_count": int(prices_count),
        "eval_count": int(eval_count),
        "val_count": int(val_count),
        "sub_count": int(sub_count),
        "cal_dup": int(cal_dup),
        "prices_dup": int(prices_dup),
        "sales_dup": int(sales_dup),
        "invalid_prices": int(invalid_prices),
        "stores": [s[0] for s in stores],
        "categories": [c[0] for c in categories],
        "departments": [d[0] for d in departments],
        "states": [s[0] for s in states],
        "total_units_overall": int(store_sales_df["total_units_sold"].sum()),
        "store_sales": store_sales_df.to_dict(orient="records"),
        "cat_sales": cat_sales_df.to_dict(orient="records"),
        "price_stats": price_stats.to_dict(orient="records")
    }
    import json
    with open(summary_file, "w") as f:
        json.dump(stats_dict, f, indent=2)

    logger.info("=== Data Cleaning & EDA Engine Completed Successfully ===")

if __name__ == "__main__":
    main()
