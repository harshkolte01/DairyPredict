import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Company Data", page_icon="📁", layout="wide")

def main():
    st.title("📁 Dairy Company Data")
    st.markdown("Comprehensive dairy sales data from three major companies: Mother Dairy, Amul, and Heritage Foods")
    
    # Auto-load data if not already loaded
    if not st.session_state.get('data_uploaded', False) or st.session_state.df is None:
        with st.spinner("Loading comprehensive dairy company data..."):
            df, success, message = DataProcessor.load_preloaded_data()
            
            if success:
                st.session_state.df = df
                st.session_state.data_uploaded = True
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                return
    
    df = st.session_state.df
    
    # Data overview section
    st.subheader("📊 Dataset Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Companies", df['Company'].nunique())
    with col3:
        st.metric("Products", df['Product'].nunique())
    with col4:
        # Ensure Date is datetime
        if df['Date'].dtype == 'object':
            df['Date'] = pd.to_datetime(df['Date'])
        date_range = (df['Date'].max() - df['Date'].min()).days
        st.metric("Date Range", f"{date_range} days")
    with col5:
        total_revenue = df['Revenue'].sum() if 'Revenue' in df.columns else (df['Quantity_Sold'] * df['Unit_Price']).sum()
        st.metric("Total Revenue", f"₹{total_revenue/1000000:.1f}M")
    
    # Company breakdown
    st.subheader("🏢 Company Analysis")
    
    company_summary = df.groupby('Company').agg({
        'Quantity_Sold': 'sum',
        'Revenue': 'sum' if 'Revenue' in df.columns else lambda x: (df.loc[x.index, 'Quantity_Sold'] * df.loc[x.index, 'Unit_Price']).sum(),
        'Product': 'nunique',
        'Date': lambda x: (x.max() - x.min()).days
    }).round(2)
    
    company_summary.columns = ['Total Quantity', 'Total Revenue (₹)', 'Products', 'Date Range (days)']
    company_summary['Total Revenue (₹M)'] = (company_summary['Total Revenue (₹)'] / 1000000).round(1)
    company_summary = company_summary.drop('Total Revenue (₹)', axis=1)
    
    st.dataframe(company_summary, use_container_width=True)
    
    # Product analysis
    st.subheader("🥛 Product Analysis")
    
    product_summary = df.groupby(['Company', 'Product']).agg({
        'Quantity_Sold': 'sum',
        'Unit_Price': 'mean',
        'Revenue': 'sum' if 'Revenue' in df.columns else lambda x: (df.loc[x.index, 'Quantity_Sold'] * df.loc[x.index, 'Unit_Price']).sum()
    }).round(2)
    
    product_summary.columns = ['Total Quantity', 'Avg Price (₹)', 'Total Revenue (₹)']
    product_summary['Revenue (₹M)'] = (product_summary['Total Revenue (₹)'] / 1000000).round(2)
    product_summary = product_summary.drop('Total Revenue (₹)', axis=1)
    
    st.dataframe(product_summary, use_container_width=True)
    
    # Visualizations
    st.subheader("📊 Data Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Company revenue comparison
        company_revenue = df.groupby('Company')['Revenue'].sum() if 'Revenue' in df.columns else df.groupby('Company').apply(lambda x: (x['Quantity_Sold'] * x['Unit_Price']).sum())
        fig = px.pie(values=company_revenue.values, names=company_revenue.index,
                   title='Revenue Distribution by Company')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product performance across companies
        product_totals = df.groupby('Product')['Quantity_Sold'].sum().reset_index()
        fig = px.bar(product_totals, x='Product', y='Quantity_Sold',
                   title='Total Quantity by Product')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time series analysis
    st.subheader("📈 Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily sales trend
        daily_sales = df.groupby('Date')['Quantity_Sold'].sum().reset_index()
        fig = px.line(daily_sales, x='Date', y='Quantity_Sold',
                    title='Daily Sales Trend (All Companies)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Company-wise monthly revenue
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M').astype(str)
        monthly_revenue = df.groupby(['Month', 'Company'])['Revenue'].sum().reset_index() if 'Revenue' in df.columns else df.groupby(['Month', 'Company']).apply(lambda x: (x['Quantity_Sold'] * x['Unit_Price']).sum()).reset_index(name='Revenue')
        fig = px.line(monthly_revenue, x='Month', y='Revenue', color='Company',
                    title='Monthly Revenue by Company')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data sample
    st.subheader("📋 Data Sample")
    st.dataframe(df.head(20), use_container_width=True)
    
    # Navigation
    st.markdown("---")
    st.subheader("🚀 Next Steps")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard.py")
    
    with col2:
        if st.button("🤖 Train Models", use_container_width=True):
            st.switch_page("pages/3_🤖_Model_Training.py")
    
    with col3:
        if st.button("📈 Forecasting", use_container_width=True):
            st.switch_page("pages/4_📈_Forecasting.py")
    
    with col4:
        if st.button("📊 Model Training", use_container_width=True):
            st.switch_page("pages/3_🤖_Model_Training.py")

if __name__ == "__main__":
    main()
