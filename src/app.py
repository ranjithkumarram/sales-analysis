import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(page_title="Superstore Sales Dashboard", page_icon="📊", layout="wide")

# Title
st.title("🛒 Superstore Sales Analysis Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("src/data/Superstore.csv")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
category = st.sidebar.multiselect("Category", options=df['Category'].unique(), default=df['Category'].unique())
subcategory = st.sidebar.multiselect("Sub-Category", options=df['Sub-Category'].unique(), default=df['Sub-Category'].unique())
region = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())
year = st.sidebar.multiselect("Year", options=df['Year'].unique(), default=df['Year'].unique())

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
st.subheader("📈 Sales Trends Over Time")
fig1 = px.line(filtered_df.groupby(['Order Date', 'Year'])['Sales'].sum().reset_index(), x='Order Date', y='Sales', color='Year', title="Sales by Date")
st.plotly_chart(fig1, use_container_width=True)

# Product Performance
st.subheader("📊 Product Performance")
fig2 = px.bar(filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False), x='Sales', y='Sub-Category', orientation='h', title="Sales by Sub-Category")
st.plotly_chart(fig2, use_container_width=True)

# Region Analysis
st.subheader("🗺️ Sales by Region")
fig3 = px.pie(filtered_df, names='Region', values='Sales', title="Sales Distribution by Region")
st.plotly_chart(fig3, use_container_width=True)

# Shipping Analysis
st.subheader("🚚 Shipping Analysis")
ship_fig = px.bar(filtered_df.groupby('Ship Mode')['Sales'].sum().reset_index().sort_values('Sales', ascending=False), x='Sales', y='Ship Mode', title="Sales by Ship Mode")
st.plotly_chart(ship_fig, use_container_width=True)

# Location Analysis (State level)
st.subheader("📍 Location Analysis")
state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
fig4 = px.bar(state_sales, x='Sales', y='State', orientation='h', title="Top 10 States by Sales")
st.plotly_chart(fig4, use_container_width=True)

# Data export
st.subheader("📥 Export Filtered Data")
csv = filtered_df.to_csv(index=False)
st.download_button("Download CSV", csv, "filtered_superstore_data.csv", "text/csv")