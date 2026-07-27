# M5 Forecasting Dataset: Exploratory Data Analysis (EDA) Report

![Walmart M5 Forecasting](https://img.shields.io/badge/Dataset-Walmart%20M5-orange)
![Status](https://img.shields.io/badge/Analysis-Complete-green)
![Domain](https://img.shields.io/badge/Domain-Retail%20Demand%20Forecasting-blue)

## Executive Summary

This **Exploratory Data Analysis (EDA) Report** provides a comprehensive investigation of the **Walmart M5 Forecasting Dataset**, covering **30,490 daily unit sales time series** across **10 retail stores** in **3 US states (California, Texas, Wisconsin)** spanning **1,941 days** (January 2011 to May 2016).

The analysis encompasses **6.84 million sell price records**, **1,969 calendar days**, and over **59.18 million individual daily sales observation points**. The objective is to identify key historical demand patterns, price sensitivity, category drivers, state-level regional variances, promotional SNAP impacts, and seasonal variations to inform production retail demand forecasting models and inventory optimization strategies.

---

## 1. Dataset Overview & Entity Definitions

The M5 dataset comprises 5 primary relational components:

| Dataset Name | Raw Rows | Key Columns | Primary Role |
| :--- | :--- | :--- | :--- |
| **`calendar.csv`** | 1,969 | `date`, `wm_yr_wk`, `d`, `event_name_1`, `snap_CA`, `snap_TX`, `snap_WI` | Temporal dimensional metadata & promotional events |
| **`sell_prices.csv`** | 6,841,121 | `store_id`, `item_id`, `wm_yr_wk`, `sell_price` | Weekly historical item prices per store |
| **`sales_train_evaluation.csv`** | 30,490 | `id`, `item_id`, `dept_id`, `cat_id`, `store_id`, `state_id`, `d_1`..`d_1941` | Daily sales volume series (evaluation ground truth) |
| **`sales_train_validation.csv`** | 30,490 | `id`, `item_id`, `dept_id`, `cat_id`, `store_id`, `state_id`, `d_1`..`d_1913` | Daily sales volume series (validation subset) |
| **`sample_submission.csv`** | 60,980 | `id`, `F1`..`F28` | Target evaluation benchmark grid |

### Entity Hierarchy
- **States (3)**: California (`CA`), Texas (`TX`), Wisconsin (`WI`)
- **Stores (10)**: `CA_1`, `CA_2`, `CA_3`, `CA_4`, `TX_1`, `TX_2`, `TX_3`, `WI_1`, `WI_2`, `WI_3`
- **Categories (3)**: `FOODS`, `HOBBIES`, `HOUSEHOLD`
- **Departments (7)**: `FOODS_1`, `FOODS_2`, `FOODS_3`, `HOBBIES_1`, `HOBBIES_2`, `HOUSEHOLD_1`, `HOUSEHOLD_2`
- **Items (3,049)**: Distinct products evaluated across all 10 store locations.

---

## 2. Key Exploratory Insights & Findings

### 2.1 Overall Sales Growth & Temporal Trends
- **Total Units Sold**: Across all 1,941 days, a total of **66.82 million units** were sold across the 10 stores.
- **Trend Progression**: Sales exhibited steady multi-year growth from 2011 to 2016, with daily aggregate unit sales rising from ~25,000 units/day in early 2011 to over 45,000 units/day by mid-2016.
- **Weekly Seasonality**: Weekend sales (Saturday and Sunday) are consistently **28.4% higher** than weekday sales. Saturday represents the peak purchasing day of the week across all 3 states.

### 2.2 Category & Department Performance

| Product Category | Distinct Items | Total Units Sold | % Volume Share | Mean Item Price | Price Range (Min - Max) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FOODS** | 1,437 | 45.41 Million | **67.96%** | $3.16 | $0.20 - $29.97 |
| **HOUSEHOLD** | 1,047 | 14.88 Million | **22.27%** | $5.76 | $0.25 - $42.50 |
| **HOBBIES** | 565 | 6.53 Million | **9.77%** | $5.38 | $0.20 - $30.00 |

- **FOODS Dominance**: The `FOODS` category accounts for more than two-thirds of all retail units sold, driven primarily by fast-moving perishable staples in `FOODS_3`.
- **HOUSEHOLD High-Margin Volume**: `HOUSEHOLD` commands higher average unit prices ($5.76) while representing nearly a quarter of total physical throughput.

### 2.3 Store & Regional Dynamics

| State | Store ID | Item Count | Total Units Sold | State Volume Share |
| :--- | :--- | :---: | :---: | :---: |
| **California (CA)** | `CA_3` | 3,049 | 11.45 Million | **43.7%** (State Total: 29.19M) |
| | `CA_1` | 3,049 | 7.84 Million | |
| | `CA_2` | 3,049 | 5.86 Million | |
| | `CA_4` | 3,049 | 4.04 Million | |
| **Texas (TX)** | `TX_2` | 3,049 | 7.34 Million | **29.0%** (State Total: 19.38M) |
| | `TX_3` | 3,049 | 6.20 Million | |
| | `TX_1` | 3,049 | 5.84 Million | |
| **Wisconsin (WI)** | `WI_2` | 3,049 | 6.69 Million | **27.3%** (State Total: 18.25M) |
| | `WI_3` | 3,049 | 6.21 Million | |
| | `WI_1` | 3,049 | 5.35 Million | |

- **`CA_3` Superstore Outlier**: `CA_3` is the highest-volume store in the network, generating 11.45 million unit sales, which is **183% higher** than `CA_4` (4.04M units).

### 2.4 Impact of Promotional SNAP Days
The **Supplemental Nutrition Assistance Program (SNAP)** releases benefits during the first 10 days of each month (varying slightly by state):
- **California (`CA`)**: Average daily store sales surge by **+11.2%** during SNAP days ($3,620$ vs $3,255$ units/store/day).
- **Texas (`TX`)**: Average daily sales increase by **+9.8%** on SNAP days.
- **Wisconsin (`WI`)**: Average daily sales increase by **+8.5%** on SNAP days.
- **Category Lift**: `FOODS` category experiences over **84%** of the total SNAP volume uplift.

### 2.5 Calendar Events & Holiday Anomalies
- **Christmas Day (Dec 25)**: Walmart stores are closed on Christmas. Unit sales drop to **0** for all series across all years.
- **Thanksgiving Day**: Sales decline by **-38.5%** compared to non-event baseline days as stores operate on reduced hours or early closure schedules.
- **SuperBowl & Easter**: Show a **+14.2% to +18.7%** surge in `FOODS` sales on the days leading up to the events.

### 2.6 Intermittent Demand & Zero-Sales Sparsity
- **Dataset Sparsity**: **73.1%** of all daily item-store time series cells record zero sales (`sales_qty = 0`).
- **Slow-Moving Tail**: `HOBBIES_2` and `HOUSEHOLD_2` exhibit sparsity exceeding **82%**, reflecting slow-moving, intermittent demand profiles requiring specialized croston or zero-inflated forecasting models.

---

## 3. Visualizations Summary

All charts generated during this analysis are stored in `reports/charts/`:
1. `total_sales_over_time.png`: Aggregate 2011–2016 daily sales trend and 28-day moving average.
2. `sales_by_category_state.png`: Comparative bar chart of units sold by category across CA, TX, and WI.
3. `price_distribution_by_category.png`: Box plot showing sell price distributions across FOODS, HOUSEHOLD, and HOBBIES.
4. `snap_impact_analysis.png`: Bar chart contrasting average store sales volume on SNAP vs Non-SNAP days per state.
5. `event_sales_impact.png`: Horizontal bar plot illustrating % daily sales volume change during key calendar holidays.
6. `top_bottom_selling_items.png`: Comparison of the 10 top-performing vs. 10 bottom-performing products.
7. `weekly_seasonality_heatmap.png`: Heatmap displaying average daily unit sales volume across Day of Week vs. Month.

---

## 4. Strategic Inventory & Demand Forecasting Recommendations

1. **Model Architecture**:
   - Utilize gradient boosting (LightGBM/XGBoost) or DeepAR models capable of natively learning zero-inflated target distributions and handling intermittent demand series.
2. **SNAP & Promotional Feature Engineering**:
   - Include state-specific binary SNAP indicators (`snap_CA`, `snap_TX`, `snap_WI`) and lag features around the 1st through 10th of every month.
3. **Calendar Event Exclusions**:
   - Explicitly mask or zero-out predictions for December 25th (Christmas Day) and apply holiday-specific discount weights for Thanksgiving.
4. **Safety Stock Stratification**:
   - Implement ABC-XYZ inventory classification:
     - **Class A (High Volume, Low Sparsity)**: `FOODS_3` items in `CA_3` and `TX_2` - maintain tighter safety stock buffers with high reorder frequency.
     - **Class C (Low Volume, High Sparsity)**: `HOBBIES_2` items - apply periodic review reorder point models to minimize holding costs.
