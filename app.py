import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_processor import DataProcessor
from utils.ui_components import UIComponents

# Set page configuration
st.set_page_config(
    page_title="DairyPredict - AI Forecasting System",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
UIComponents.apply_custom_css()

# Initialize session state and auto-load data
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = False
if 'forecasts' not in st.session_state:
    st.session_state.forecasts = {}

# Auto-load preloaded data if not already loaded
if not st.session_state.data_uploaded:
    df, success, message = DataProcessor.load_preloaded_data()
    if success:
        st.session_state.df = df
        st.session_state.data_uploaded = True

def main():
    # Create page header
    UIComponents.create_page_header(
        "DairyPredict AI Forecasting System",
        "Advanced machine learning platform for dairy demand forecasting and production optimization"
    )
    
    # Create navigation sidebar
    UIComponents.create_navigation_sidebar()
    
    # Progress indicator
    step_names = ["Data Loading", "Model Training", "Forecasting", "Analysis"]
    current_step = 1
    if st.session_state.get('data_uploaded', False):
        current_step = 2
    if st.session_state.get('models_trained', False):
        current_step = 3
    if st.session_state.get('forecasts', {}):
        current_step = 4
    
    with st.sidebar:
        st.markdown("---")
        UIComponents.create_progress_indicator(current_step, 4, step_names)
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        # Status indicators
        if st.session_state.get('data_uploaded', False):
            st.markdown(UIComponents.create_status_indicator("✅ Data Loaded", "success"), unsafe_allow_html=True)
            if st.session_state.df is not None:
                st.markdown(f"📊 **{len(st.session_state.df):,}** records")
                if 'Company' in st.session_state.df.columns:
                    companies = st.session_state.df['Company'].nunique()
                    st.markdown(f"🏢 **{companies}** companies")
                    products = st.session_state.df['Product'].nunique()
                    st.markdown(f"🥛 **{products}** products")
        else:
            st.markdown(UIComponents.create_status_indicator("⚠️ No Data", "warning"), unsafe_allow_html=True)
            
        if st.session_state.get('models_trained', False):
            st.markdown(UIComponents.create_status_indicator("✅ Models Ready", "success"), unsafe_allow_html=True)
        else:
            st.markdown(UIComponents.create_status_indicator("ℹ️ Models Pending", "info"), unsafe_allow_html=True)

    # Main content area
    if st.session_state.get('data_uploaded', False) and st.session_state.df is not None:
        # Data summary section
        st.markdown(UIComponents.create_section_header("📊 Data Overview", "📊"), unsafe_allow_html=True)
        UIComponents.create_data_summary_card(st.session_state.df)
        
        # Company showcase
        st.markdown(UIComponents.create_section_header("🏢 Loaded Companies", "🏢"), unsafe_allow_html=True)
        if 'Company' in st.session_state.df.columns:
            companies = st.session_state.df['Company'].unique()
            cols = st.columns(len(companies))
            
            company_colors = ['#667eea', '#764ba2', '#f093fb']
            for i, (company, col) in enumerate(zip(companies, cols)):
                with col:
                    # Calculate company metrics
                    company_data = st.session_state.df[st.session_state.df['Company'] == company]
                    total_products = company_data['Product'].nunique()
                    total_records = len(company_data)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {company_colors[i % len(company_colors)]}, {company_colors[(i+1) % len(company_colors)]}); 
                                color: white; padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;">
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.2rem;">🏢 {company}</h3>
                        <p style="margin: 0; opacity: 0.9;">{total_products} Products</p>
                        <p style="margin: 0; opacity: 0.9;">{total_records:,} Records</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Products showcase
        st.markdown(UIComponents.create_section_header("🥛 Available Products", "🥛"), unsafe_allow_html=True)
        if 'Product' in st.session_state.df.columns:
            products = sorted(st.session_state.df['Product'].unique())
            
            # Create product grid
            cols_per_row = 4
            for i in range(0, len(products), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, product in enumerate(products[i:i+cols_per_row]):
                    with cols[j]:
                        # Calculate product metrics
                        product_data = st.session_state.df[st.session_state.df['Product'] == product]
                        total_quantity = product_data['Quantity_Sold'].sum() if 'Quantity_Sold' in product_data.columns else 0
                        
                        st.markdown(f"""
                        <div style="background: white; border: 2px solid #e1e5e9; padding: 1rem; 
                                    border-radius: 8px; text-align: center; transition: all 0.3s ease;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">🥛 {product}</h4>
                            <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">{total_quantity:,.0f} units sold</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    else:
        # Welcome section for new users
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 3rem 2rem;">
                <h2 style="color: #2c3e50; margin-bottom: 1rem;">Welcome to DairyPredict</h2>
                <p style="font-size: 1.1rem; color: #7f8c8d; line-height: 1.6; margin-bottom: 2rem;">
                    Transform your dairy business with AI-powered demand forecasting. 
                    Our advanced system analyzes historical data from multiple dairy companies 
                    to provide accurate predictions and optimization recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Getting started section
            st.markdown(UIComponents.create_section_header("🚀 Getting Started", "🚀"), unsafe_allow_html=True)
            
            steps = [
                ("1️⃣", "Load Data", "Start with our pre-loaded multi-company dataset", "📁 Company Data"),
                ("2️⃣", "Train Models", "Train AI models using Prophet time series analysis", "🤖 Model Training"),
                ("3️⃣", "Generate Forecasts", "Create demand predictions and optimization plans", "📈 Forecasting"),
                ("4️⃣", "Analyze Results", "Review comprehensive reports and insights", "📋 Reports")
            ]
            
            for icon, title, desc, page in steps:
                st.markdown(f"""
                <div style="background: #f8f9fa; border-left: 4px solid #667eea; 
                            padding: 1.5rem; margin-bottom: 1rem; border-radius: 0 8px 8px 0;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
                        <h4 style="margin: 0; color: #2c3e50;">{title}</h4>
                    </div>
                    <p style="margin: 0 0 0.5rem 3rem; color: #7f8c8d;">{desc}</p>
                    <p style="margin: 0 0 0 3rem;"><strong>→ Go to {page}</strong></p>
                </div>
                """, unsafe_allow_html=True)
    
    # Feature showcase
    UIComponents.create_feature_showcase()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #7f8c8d;">
        <p>🥛 <strong>DairyPredict</strong> - AI-Powered Dairy Demand Forecasting System</p>
        <p>Built with Streamlit, Prophet, and advanced machine learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
