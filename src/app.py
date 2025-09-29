import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page config MUST be the first Streamlit call
st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

# Title
st.title("Superstore Sales Analysis Dashboard")
st.markdown("---")

# Data loader
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load Superstore dataset and ensure required columns are well-typed.

    - Reads data relative to this file for robust execution regardless of CWD
    - Parses dates with dayfirst=True to match the dataset format (e.g., 31/10/2015)
    - Adds a Year column if missing
    """
    data_path = Path(__file__).resolve().parent / "data" / "Superstore.csv"
    df = pd.read_csv(data_path)

    # Ensure Order Date is datetime (dayfirst because dataset uses DD/MM/YYYY)
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce", dayfirst=True)
        df = df.sort_values("Order Date")

    # Add Year if missing (from Order Date)
    if "Year" not in df.columns and "Order Date" in df.columns:
        df["Year"] = df["Order Date"].dt.year

    # Normalize numeric columns if they exist
    for col in ["Sales", "Profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Coerce Year to integer where possible for consistent filtering and coloring
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")

    return df


df = load_data()

# Sidebar: attribution and filters
st.sidebar.header("Filters")
st.sidebar.markdown("**Owner/Author:** Ranjith Kumar Ramasamy")


def multiselect_for_column(frame: pd.DataFrame, col: str, label: str, *, numeric_int: bool = False):
    """Create a multiselect for a given column if present; otherwise return None.
    If numeric_int is True, convert options to distinct ints for display and selection.
    """
    if col not in frame.columns:
        st.sidebar.info(f"Column '{col}' not found; showing all data for this dimension.")
        return None

    series = frame[col].dropna()
    if numeric_int:
        series = pd.to_numeric(series, errors="coerce").dropna().astype(int)
    options = sorted(series.unique().tolist(), key=lambda x: (str(x)))
    selection = st.sidebar.multiselect(label, options=options, default=options)
    return selection


category_sel = multiselect_for_column(df, "Category", "Category")
subcategory_sel = multiselect_for_column(df, "Sub-Category", "Sub-Category")
region_sel = multiselect_for_column(df, "Region", "Region")
year_sel = multiselect_for_column(df, "Year", "Year", numeric_int=True)

# Build filtered dataframe defensively (apply only existing filters)
filtered_df = df.copy()
if category_sel is not None:
    filtered_df = filtered_df[filtered_df["Category"].isin(category_sel)]
if subcategory_sel is not None:
    filtered_df = filtered_df[filtered_df["Sub-Category"].isin(subcategory_sel)]
if region_sel is not None:
    filtered_df = filtered_df[filtered_df["Region"].isin(region_sel)]
if year_sel is not None and "Year" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Year"].isin(year_sel)]

# Metrics
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Sales"].sum() if "Sales" in filtered_df.columns else 0.0
total_profit = filtered_df["Profit"].sum() if "Profit" in filtered_df.columns else 0.0
if "Order ID" in filtered_df.columns:
    total_orders = filtered_df["Order ID"].nunique()
else:
    total_orders = len(filtered_df)

avg_profit_margin = (total_profit / total_sales * 100) if total_sales and total_sales > 0 else 0

with col1:
    st.metric("Total Sales", f"${total_sales:,.2f}")
with col2:
    st.metric("Total Profit", f"${total_profit:,.2f}")
with col3:
    st.metric("Total Orders", int(total_orders))
with col4:
    st.metric("Avg Profit Margin", f"{avg_profit_margin:.2f}%")

st.markdown("---")

# Sales Trends
st.subheader("Sales Trends Over Time")
if all(c in filtered_df.columns for c in ["Order Date", "Sales"]) and not filtered_df.empty:
    group_cols = ["Order Date"] + (["Year"] if "Year" in filtered_df.columns else [])
    trend_df = (
        filtered_df.dropna(subset=["Order Date", "Sales"])\
                   .groupby(group_cols)["Sales"].sum()\
                   .reset_index()
    )
    if "Year" in trend_df.columns:
        fig1 = px.line(trend_df, x="Order Date", y="Sales", color="Year", title="Sales by Date")
    else:
        fig1 = px.line(trend_df, x="Order Date", y="Sales", title="Sales by Date")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Required columns for this chart are missing or no data after filtering.")

# Product Performance
st.subheader("Product Performance")
if all(c in filtered_df.columns for c in ["Sub-Category", "Sales"]) and not filtered_df.empty:
    prod_df = (
        filtered_df.groupby("Sub-Category")["Sales"].sum()\
                   .reset_index()\
                   .sort_values("Sales", ascending=False)
    )
    fig2 = px.bar(prod_df, x="Sales", y="Sub-Category", orientation="h", title="Sales by Sub-Category")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Required columns for this chart are missing or no data after filtering.")

# Region Analysis
st.subheader("Sales by Region")
if all(c in filtered_df.columns for c in ["Region", "Sales"]) and not filtered_df.empty:
    reg_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
    fig3 = px.pie(reg_df, names="Region", values="Sales", title="Sales Distribution by Region")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Required columns for this chart are missing or no data after filtering.")

# Shipping Analysis
st.subheader("Shipping Analysis")
if all(c in filtered_df.columns for c in ["Ship Mode", "Sales"]) and not filtered_df.empty:
    ship_df = (
        filtered_df.groupby("Ship Mode")["Sales"].sum()\
                   .reset_index()\
                   .sort_values("Sales", ascending=False)
    )
    ship_fig = px.bar(ship_df, x="Sales", y="Ship Mode", title="Sales by Ship Mode")
    st.plotly_chart(ship_fig, use_container_width=True)
else:
    st.info("Required columns for this chart are missing or no data after filtering.")

# Location Analysis (State level)
st.subheader("Location Analysis")
if all(c in filtered_df.columns for c in ["State", "Sales"]) and not filtered_df.empty:
    state_sales = (
        filtered_df.groupby("State")["Sales"].sum()\
                   .reset_index()\
                   .sort_values("Sales", ascending=False)\
                   .head(10)
    )
    fig4 = px.bar(state_sales, x="Sales", y="State", orientation="h", title="Top 10 States by Sales")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Required columns for this chart are missing or no data after filtering.")

# Data export
st.subheader("Export Filtered Data")
csv = filtered_df.to_csv(index=False)
st.download_button("Download CSV", csv, "filtered_superstore_data.csv", "text/csv")
