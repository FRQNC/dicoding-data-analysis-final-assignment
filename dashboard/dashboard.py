# Import Libraries
import streamlit as st
import pandas as pd

# Load data
main_df = pd.read_csv('main_data.csv')

# Convert timestamp to datetime
main_df['order_purchase_timestamp'] = pd.to_datetime(main_df['order_purchase_timestamp'])

# Sidebar layout
with st.sidebar:
    st.header("Filter Options")

    # Date Range Filter
    min_date = main_df['order_purchase_timestamp'].min().date()
    max_date = main_df['order_purchase_timestamp'].max().date()
    start_date, end_date = st.date_input(
        label="Select Purchase Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Daily or Monthly Filter
    daily_or_monthly = st.selectbox("Select Daily or Monthly View", ("Monthly", "Daily"))

    # Order Status Filter
    order_status_options = main_df['order_status'].unique().tolist()
    selected_status = st.multiselect("Select Order Status", order_status_options, default=[])

    # Product Category Filter
    product_categories = main_df['product_category_name'].unique().tolist()
    selected_categories = st.multiselect("Select Product Categories", product_categories, default=[])

# Filter the dataframe
filtered_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# Apply filters only if selected
if selected_status:
    filtered_df = filtered_df[filtered_df['order_status'].isin(selected_status)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['product_category_name'].isin(selected_categories)]

# Calculate KPIs
total_revenue = filtered_df['total_revenue'].max()
total_orders = filtered_df['order_id'].nunique()
total_customers = filtered_df['customer_unique_id'].nunique()
average_order_value = total_revenue / total_orders if total_orders > 0 else 0

# Sales and total orders over time
sales_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period("M"))['price'].sum()
sales_over_time.index = sales_over_time.index.to_timestamp()

orders_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period("M"))['order_id'].nunique()
orders_over_time.index = orders_over_time.index.to_timestamp()

if daily_or_monthly == "Daily":
    sales_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date)['price'].sum()
    orders_over_time = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date)['order_id'].nunique()

# Orders by status
orders_by_status = filtered_df['order_status'].value_counts()

# Revenue by category
revenue_by_category = filtered_df.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)

# Total orders by category
orders_by_category = filtered_df['product_category_name'].value_counts().head(10)

# Dashboard Title
st.title("E-commerce Sales Dashboard")

# KPI Section
st.subheader("Key Performance Indicators")
# First row: Total Revenue only
st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
# Second row: Other KPIs
kpi_row = st.columns(3)
kpi_row[0].metric("Total Orders", total_orders)
kpi_row[1].metric("Total Customers", total_customers)
kpi_row[2].metric("Avg Order Value", f"R$ {average_order_value:,.2f}")

# Sales Trend Section
st.subheader("Sales Over Time")
st.line_chart(sales_over_time)

# Orders Trend Section
st.subheader("Number of Orders Over Time")
st.line_chart(orders_over_time)

# Top Categories and Order Status (Conditional)
if len(selected_categories) != 1:
    st.subheader("Top 10 Categories by Revenue")
    st.bar_chart(revenue_by_category)

    st.subheader("Top 10 Categories by Number of Orders")
    st.bar_chart(orders_by_category)

if len(selected_status) != 1:
    st.subheader("Orders by Status")
    st.bar_chart(orders_by_status)