import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

# Title
st.title("Superstore Sales Analysis Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("src/data/Superstore.csv")
    # Ensure Order Date is a datetime and data is sorted for proper time-series handling
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
        df = df.sort_values('Order Date')
        # Backfill Year if it's missing
        if 'Year' not in df.columns:
            df['Year'] = df['Order Date'].dt.year
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
st.sidebar.markdown("**Owner/Author:** ranjith")

# Build options lists without NaN to avoid Streamlit multiselect default mismatch
cat_options = df['Category'].dropna().unique().tolist()
cat_options = sorted(cat_options, key=lambda x: str(x))
category = st.sidebar.multiselect("Category", options=cat_options, default=cat_options)

subcat_options = df['Sub-Category'].dropna().unique().tolist()
subcat_options = sorted(subcat_options, key=lambda x: str(x))
subcategory = st.sidebar.multiselect("Sub-Category", options=subcat_options, default=subcat_options)

region_options = df['Region'].dropna().unique().tolist()
region_options = sorted(region_options, key=lambda x: str(x))
region = st.sidebar.multiselect("Region", options=region_options, default=region_options)

year_options = pd.Series(df['Year']).dropna().unique().tolist()
try:
    year_options = sorted(year_options)
except TypeError:
    year_options = sorted(year_options, key=lambda x: str(x))
year = st.sidebar.multiselect("Year", options=year_options, default=year_options)

# Filter data
filtered_df = df[
    (df['Category'].isin(category)) &
    (df['Sub-Category'].isin(subcategory)) &
    (df['Region'].isin(region)) &
    (df['Year'].isin(year))
]

# Metrics
col1, col2, col3, col4 = st.columns(4)
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = len(filtered_df)
avg_profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

with col1:
    st.metric("Total Sales", f"${total_sales:,.2f}")
with col2:
    st.metric("Total Profit", f"${total_profit:,.2f}")
with col3:
    st.metric("Total Orders", total_orders)
with col4:
    st.metric("Avg Profit Margin", f"{avg_profit_margin:.2f}%")

st.markdown("---")

# Sales Trends
st.subheader("Sales Trends Over Time")
fig1 = px.line(filtered_df.groupby(['Order Date', 'Year'])['Sales'].sum().reset_index(), x='Order Date', y='Sales', color='Year', title="Sales by Date")
st.plotly_chart(fig1, use_container_width=True)

# Product Performance
st.subheader("Product Performance")
fig2 = px.bar(filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False), x='Sales', y='Sub-Category', orientation='h', title="Sales by Sub-Category")
st.plotly_chart(fig2, use_container_width=True)

# Region Analysis
st.subheader("Sales by Region")
fig3 = px.pie(filtered_df, names='Region', values='Sales', title="Sales Distribution by Region")
st.plotly_chart(fig3, use_container_width=True)

# Shipping Analysis
st.subheader("Shipping Analysis")
ship_fig = px.bar(filtered_df.groupby('Ship Mode')['Sales'].sum().reset_index().sort_values('Sales', ascending=False), x='Sales', y='Ship Mode', title="Sales by Ship Mode")
st.plotly_chart(ship_fig, use_container_width=True)

# Location Analysis (State level)
st.subheader("Location Analysis")
state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
fig4 = px.bar(state_sales, x='Sales', y='State', orientation='h', title="Top 10 States by Sales")
st.plotly_chart(fig4, use_container_width=True)

# Data export
st.subheader("Export Filtered Data")
csv = filtered_df.to_csv(index=False)
st.download_button("Download CSV", csv, "filtered_superstore_data.csv", "text/csv")