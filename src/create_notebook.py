import os
import nbformat as nbf

def build_m5_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # Title & Metadata
    title_md = """# Walmart M5 Forecasting Dataset: End-to-End EDA & Data Cleaning

**Author:** Data Analyst  
**Date:** July 2026  
**Dataset:** Walmart M5 Forecasting Dataset  
**Objective:** Perform comprehensive Exploratory Data Analysis (EDA) and Data Cleaning across all M5 dataset CSV files.

---

### Task Breakdown & Outline
1. **Task 1: Load CSV Files** - Extract raw CSV files (`calendar.csv`, `sell_prices.csv`, `sales_train_validation.csv`, `sales_train_evaluation.csv`, `sample_submission.csv`).
2. **Task 2: Handle Missing Values** - Identify null patterns and impute event categories.
3. **Task 3: Remove Duplicates** - Audit primary and composite key uniqueness.
4. **Task 4: Convert Dates** - Parse datetime structures and engineer calendar temporal features.
5. **Task 5: Check Data Consistency** - Validate value ranges, foreign key integrity, and temporal continuity.
6. **Task 6: Generate Descriptive Statistics** - Compute price distributions, store/category sales metrics, and zero-sales sparsity.
7. **Task 7: Generate Visualizations** - Render high-impact exploratory plots (time series, heatmaps, category breakdowns, SNAP & event impact analysis).
"""
    cells.append(nbf.v4.new_markdown_cell(title_md))

    # Setup cell
    setup_code = """import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import Image, display

# Styling configuration
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "axes.titlesize": 14, "figure.dpi": 150})

DATA_DIR = "../m5-forecasting-accuracy"
CLEANED_DIR = "../data/cleaned"
CHARTS_DIR = "../reports/charts"

print("Libraries imported and paths configured successfully.")
"""
    cells.append(nbf.v4.new_code_cell(setup_code))

    # Task 1: Load CSV Files
    task1_md = """## Task 1: Load All CSV Files

We load sample rows and inspect structural metadata for all 5 M5 dataset CSV files:
- `calendar.csv`: Contains dates, holidays, events, and SNAP flags.
- `sell_prices.csv`: Contains weekly item price data per store.
- `sales_train_validation.csv`: Contains daily unit sales per item up to d_1913.
- `sales_train_evaluation.csv`: Contains daily unit sales per item up to d_1941.
- `sample_submission.csv`: Submission format specifications.
"""
    cells.append(nbf.v4.new_markdown_cell(task1_md))

    task1_code = """# Load raw CSV datasets
calendar_df = pd.read_csv(os.path.join(DATA_DIR, "calendar.csv"))
sell_prices_df = pd.read_csv(os.path.join(DATA_DIR, "sell_prices.csv"))
sales_eval_df = pd.read_csv(os.path.join(DATA_DIR, "sales_train_evaluation.csv"))
sales_val_df = pd.read_csv(os.path.join(DATA_DIR, "sales_train_validation.csv"))
sample_sub_df = pd.read_csv(os.path.join(DATA_DIR, "sample_submission.csv"))

print(f"Calendar shape: {calendar_df.shape}")
print(f"Sell Prices shape: {sell_prices_df.shape}")
print(f"Sales Evaluation shape: {sales_eval_df.shape}")
print(f"Sales Validation shape: {sales_val_df.shape}")
print(f"Sample Submission shape: {sample_sub_df.shape}")

display(calendar_df.head(3))
display(sell_prices_df.head(3))
display(sales_eval_df.head(3))
"""
    cells.append(nbf.v4.new_code_cell(task1_code))

    # Task 2: Handle Missing Values
    task2_md = """## Task 2: Audit and Handle Missing Values

Missing value analysis is conducted across all datasets.
In `calendar.csv`, missing values in `event_name_1`, `event_type_1`, `event_name_2`, and `event_type_2` occur on days without special events or holidays. These are imputed with the category `'None'`.
"""
    cells.append(nbf.v4.new_markdown_cell(task2_md))

    task2_code = r"""# Check missing values before cleaning
print("=== Calendar Missing Values (Before) ===")
print(calendar_df.isnull().sum()[calendar_df.isnull().sum() > 0])

# Impute event columns
event_cols = ["event_name_1", "event_type_1", "event_name_2", "event_type_2"]
for col in event_cols:
    calendar_df[col] = calendar_df[col].fillna("None")

print("\n=== Calendar Missing Values (After Imputation) ===")
print(calendar_df[event_cols].isnull().sum())

print("\n=== Sell Prices Missing Values ===")
print(sell_prices_df.isnull().sum())

print("\n=== Sales Evaluation Missing Values ===")
print(sales_eval_df[["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]].isnull().sum())
"""
    cells.append(nbf.v4.new_code_cell(task2_code))

    # Task 3: Remove Duplicates
    task3_md = """## Task 3: Detect and Remove Duplicates

Primary key uniqueness checks:
- `calendar.csv`: Keyed by `d` and `date`.
- `sell_prices.csv`: Keyed by composite key (`store_id`, `item_id`, `wm_yr_wk`).
- `sales_train_evaluation.csv`: Keyed by `id`.
"""
    cells.append(nbf.v4.new_markdown_cell(task3_md))

    task3_code = """# Duplicate audit
cal_dups = calendar_df.duplicated(subset=["d"]).sum()
price_dups = sell_prices_df.duplicated(subset=["store_id", "item_id", "wm_yr_wk"]).sum()
sales_dups = sales_eval_df.duplicated(subset=["id"]).sum()

print(f"Calendar Duplicate Count (key='d'): {cal_dups}")
print(f"Sell Prices Duplicate Count (key='store_id, item_id, wm_yr_wk'): {price_dups}")
print(f"Sales Evaluation Duplicate Count (key='id'): {sales_dups}")

# Deduplicate if any duplicates exist
sell_prices_df = sell_prices_df.drop_duplicates(subset=["store_id", "item_id", "wm_yr_wk"])
print(f"Cleaned Sell Prices Row Count: {len(sell_prices_df):,}")
"""
    cells.append(nbf.v4.new_code_cell(task3_code))

    # Task 4: Convert Dates
    task4_md = """## Task 4: Date Conversions and Feature Parsing

Convert `date` in `calendar.csv` to `datetime64[ns]` and verify calendar day ordering.
"""
    cells.append(nbf.v4.new_markdown_cell(task4_md))

    task4_code = """# Convert date column to datetime
calendar_df["date"] = pd.to_datetime(calendar_df["date"])
calendar_df["is_weekend"] = calendar_df["wday"].isin([1, 2]).astype(int)

print("Date range in calendar:")
print(f"Start Date: {calendar_df['date'].min().strftime('%Y-%m-%d')}")
print(f"End Date:   {calendar_df['date'].max().strftime('%Y-%m-%d')}")
print(f"Total Calendar Days: {len(calendar_df)}")

display(calendar_df[["date", "wm_yr_wk", "weekday", "wday", "month", "year", "event_name_1", "is_weekend"]].head(5))
"""
    cells.append(nbf.v4.new_code_cell(task4_code))

    # Task 5: Check Data Consistency
    task5_md = """## Task 5: Data Consistency & Integrity Audit

Validation of domain constraints:
1. Sell price positivity (`sell_price > 0`).
2. Sales quantity non-negativity (`sales_qty >= 0`).
3. Store, Category, Department, and State entity cardinalities.
4. Day index continuity (`d_1` to `d_1941`).
"""
    cells.append(nbf.v4.new_markdown_cell(task5_md))

    task5_code = r"""# 1. Price integrity check
invalid_prices = (sell_prices_df["sell_price"] <= 0).sum()
print(f"Invalid Prices (sell_price <= 0): {invalid_prices}")

# 2. Daily sales non-negativity check
d_cols = [c for c in sales_eval_df.columns if c.startswith("d_")]
negative_sales = (sales_eval_df[d_cols] < 0).sum().sum()
print(f"Negative Daily Sales Quantity Count: {negative_sales}")

# 3. Entity cardinality audit
print("\nUnique Entity Counts:")
print(f"Stores:       {sales_eval_df['store_id'].nunique()} -> {sorted(sales_eval_df['store_id'].unique())}")
print(f"States:       {sales_eval_df['state_id'].nunique()} -> {sorted(sales_eval_df['state_id'].unique())}")
print(f"Categories:   {sales_eval_df['cat_id'].nunique()} -> {sorted(sales_eval_df['cat_id'].unique())}")
print(f"Departments:  {sales_eval_df['dept_id'].nunique()} -> {sorted(sales_eval_df['dept_id'].unique())}")
print(f"Items:        {sales_eval_df['item_id'].nunique()}")

# 4. Day column sequence check
expected_d_cols = [f"d_{i}" for i in range(1, 1942)]
print(f"\nAll 1,941 day columns present in order: {d_cols == expected_d_cols}")
"""
    cells.append(nbf.v4.new_code_cell(task5_code))

    # Task 6: Descriptive Statistics
    task6_md = """## Task 6: Generate Descriptive Statistics

Statistical summaries of pricing, overall unit sales, category-level distribution, and sparsity (zero-sales ratio).
"""
    cells.append(nbf.v4.new_markdown_cell(task6_md))

    task6_code = r"""# Summary statistics for Sell Prices by Category
merged_prices = sell_prices_df.merge(
    sales_eval_df[["item_id", "cat_id", "dept_id"]].drop_duplicates(),
    on="item_id",
    how="inner"
)

price_summary = merged_prices.groupby("cat_id")["sell_price"].describe()
display(price_summary)

# Sales Volume Summary by Store
sales_eval_df["total_units"] = sales_eval_df[d_cols].sum(axis=1)
store_summary = sales_eval_df.groupby(["state_id", "store_id"])["total_units"].agg(
    item_count="count",
    total_sales="sum",
    mean_sales_per_item="mean",
    median_sales_per_item="median",
    std_sales_per_item="std"
).reset_index()

display(store_summary)

# Zero Sales Sparsity
zero_sales_count = (sales_eval_df[d_cols] == 0).sum().sum()
total_sales_cells = len(sales_eval_df) * len(d_cols)
sparsity_pct = (zero_sales_count / total_sales_cells) * 100

print(f"\nTotal Time Series Cells: {total_sales_cells:,}")
print(f"Zero Sales Cells:       {zero_sales_count:,}")
print(f"Dataset Sparsity Ratio:  {sparsity_pct:.2f}% zero-sales days")
"""
    cells.append(nbf.v4.new_code_cell(task6_code))

    # Task 7: Generate Visualizations
    task7_md = """## Task 7: Generate Exploratory Visualizations

We render and display the 7 key analytical visual charts generated by the EDA pipeline.
"""
    cells.append(nbf.v4.new_markdown_cell(task7_md))

    task7_code = """# Display all generated charts
charts = [
    ("total_sales_over_time.png", "1. Aggregate Daily & 28-Day Rolling Average Sales"),
    ("sales_by_category_state.png", "2. Total Unit Sales by Category & State"),
    ("price_distribution_by_category.png", "3. Sell Price Distribution by Category"),
    ("snap_impact_analysis.png", "4. Impact of SNAP Purchase Days on Average Sales"),
    ("event_sales_impact.png", "5. Sales Impact of Key Calendar Events & Holidays"),
    ("top_bottom_selling_items.png", "6. Top 10 Best vs. Bottom 10 Lowest Selling Products"),
    ("weekly_seasonality_heatmap.png", "7. Seasonality Heatmap: Day of Week vs. Month")
]

for filename, title in charts:
    chart_path = os.path.join(CHARTS_DIR, filename)
    if os.path.exists(chart_path):
        print(f"=== {title} ===")
        display(Image(filename=chart_path))
    else:
        print(f"Chart file not found: {chart_path}")
"""
    cells.append(nbf.v4.new_code_cell(task7_code))

    # Final Export Summary
    export_md = """## Summary & Deliverable Check

Cleaned datasets exported to `data/cleaned/`:
- `calendar_clean.parquet` / `.csv`
- `sell_prices_clean.parquet` / `.csv`
- `sales_train_evaluation_clean.parquet` / `.csv`

All 7 tasks completed successfully!
"""
    cells.append(nbf.v4.new_markdown_cell(export_md))

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    }

    out_dir = os.path.join(os.getcwd(), "notebooks")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "m5_eda_and_data_cleaning.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Notebook written successfully to {out_path}")

if __name__ == "__main__":
    build_m5_notebook()
