
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

from data_processing import load_data, clean_data, transform_data, validate_data
from analytics import (
    calculate_rfm,
    get_rfm_segment_meaning,
    calculate_clv,
    get_sales_trends,
    get_top_products,
    get_geographic_distribution
)

# Debugging information
print("Python executable:", sys.executable)
print("Python path:", sys.path)

def main():
    """Main function to run the Streamlit dashboard."""
    st.set_page_config(
        page_title="Customer Analytics Dashboard",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Sidebar ---
    st.sidebar.title("Navigation")
    st.sidebar.info(
        "Upload your customer transaction data in CSV format. "
        "The application will perform various analyses to provide customer intelligence."
    )
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    st.sidebar.markdown("---")
    st.sidebar.header("About")
    st.sidebar.info(
        "This dashboard is designed for e-commerce businesses to "
        "gain insights into their customer base and identify growth opportunities."
    )

    if uploaded_file is None:
        st.info("Please upload a CSV file to begin analysis.")
        st.subheader("Expected CSV Format:")
        st.code("""
        InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
        536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,12/1/2010 8:26,2.55,17850,United Kingdom
        ...
        """, language='csv')
        return

    # --- Data Loading and Processing ---
    with st.spinner('Loading and processing data...'):
        df = load_data(uploaded_file)
        if df is None:
            st.error("Failed to load the data. Please check the file format.")
            return

        missing_cols = validate_data(df)
        if missing_cols:
            st.error(f"The uploaded file is missing the following required columns: {', '.join(missing_cols)}")
            return

        df = clean_data(df)
        df = transform_data(df)

    st.success("Data loaded and processed successfully!")

    # --- Main Dashboard ---
    st.title("Business Intelligence Dashboard")
    st.markdown("An overview of key performance indicators and sales metrics.")

    # --- KPIs ---
    total_revenue = df['TotalPrice'].sum()
    total_customers = df['CustomerID'].nunique()
    total_orders = df['InvoiceNo'].nunique()
    avg_order_value = total_revenue / total_orders

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Customers", f"{total_customers:,}")
    col3.metric("Total Orders", f"{total_orders:,}")
    col4.metric("Avg. Order Value", f"${avg_order_value:,.2f}")

    st.markdown("---")

    # --- Tabs for Different Analyses ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Sales Performance",
        "Customer Segmentation (RFM)",
        "Customer Lifetime Value (CLV)",
        "Geographic Analysis"
    ])

    with tab1:
        st.header("Sales Performance Analysis")

        # Sales Trends
        st.subheader("Revenue Trends")
        freq = st.selectbox("Select Trend Frequency", ['Daily', 'Weekly', 'Monthly', 'Quarterly'], index=2)
        freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q'}
        sales_trends = get_sales_trends(df, freq=freq_map[freq])
        sales_trends_df = sales_trends.reset_index()
        fig = px.line(sales_trends_df, x='InvoiceDate', y='TotalPrice', title=f"{freq} Revenue Trends")
        st.plotly_chart(fig, use_container_width=True)

        # Top Products
        st.subheader("Top Selling Products")
        top_n = st.slider("Select number of top products", 5, 20, 10)
        top_products = get_top_products(df, top_n=top_n)
        top_products_df = top_products.reset_index()
        fig = px.bar(top_products_df, x='Description', y='Quantity', title=f"Top {top_n} Selling Products")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Customer Segmentation (RFM Analysis)")
        with st.spinner("Calculating RFM scores..."):
            rfm_df = calculate_rfm(df)
            rfm_df['Segment'] = rfm_df.apply(get_rfm_segment_meaning, axis=1)

        st.subheader("RFM Score Distribution")
        fig = px.scatter(rfm_df, x='Recency', y='Frequency', color='MonetaryValue',
                         size='RFM_Score', hover_name=rfm_df.index,
                         title="RFM Analysis",
                         color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Customer Segments")
        segment_counts = rfm_df['Segment'].value_counts()
        fig_pie = px.pie(values=segment_counts.values, names=segment_counts.index,
                         title="Customer Segment Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        st.dataframe(rfm_df)

    with tab3:
        st.header("Customer Lifetime Value (CLV)")
        with st.spinner("Calculating CLV..."):
            clv_df = calculate_clv(df)

        st.subheader("Top Customers by CLV")
        st.dataframe(clv_df.head(10))

        st.subheader("CLV Distribution")
        fig = px.histogram(clv_df, x="clv", nbins=50, title="Customer Lifetime Value Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.header("Geographic Sales Distribution")
        geo_dist = get_geographic_distribution(df)
        geo_df = geo_dist.reset_index()

        fig = px.choropleth(geo_df, locations="Country",
                            locationmode='country names', color="TotalPrice",
                            hover_name="Country",
                            color_continuous_scale=px.colors.sequential.Plasma,
                            title="Sales by Country")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sales Data by Country")
        st.dataframe(geo_df)

if __name__ == "__main__":
    main()
