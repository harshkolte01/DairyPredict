"""
UI Components and Styling for Dairy Prediction App
This module provides consistent UI components and styling across all pages.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

class UIComponents:
    """Class containing reusable UI components and styling."""
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling to the Streamlit app."""
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main app styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Custom font for the entire app */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Card styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border: 1px solid #e1e5e9;
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
            margin: 0;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #7f8c8d;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Status indicators */
        .status-success {
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .status-warning {
            background: linear-gradient(135deg, #fdcb6e, #e17055);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .status-info {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        /* Section styling */
        .section-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            border: 1px solid #e1e5e9;
            margin-bottom: 2rem;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f1f3f4;
        }
        
        .section-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        /* Selectbox and input styling */
        .stSelectbox > div > div {
            border-radius: 8px;
            border: 2px solid #e1e5e9;
        }
        
        .stMultiSelect > div > div {
            border-radius: 8px;
            border: 2px solid #e1e5e9;
        }
        
        /* Chart container */
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
            border: 1px solid #e1e5e9;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        .chart-container h4 {
            margin: 0 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f1f3f4;
        }
        
        /* Enhanced dataframe styling */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        /* Improved metric cards */
        .metric-card-enhanced {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1));
            transform: translateX(100px);
            transition: transform 0.3s ease;
        }
        
        .metric-card-enhanced:hover::before {
            transform: translateX(-100px);
        }
        
        .metric-card-enhanced:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* Alert styling */
        .alert-success {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .alert-info {
            background: linear-gradient(135deg, #d1ecf1, #bee5eb);
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_page_header(title, subtitle, icon="🥛"):
        """Create a consistent page header."""
        st.markdown(f"""
        <div class="main-header">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_metric_card(value, label, delta=None, delta_color="normal"):
        """Create a styled metric card."""
        delta_html = ""
        if delta is not None:
            color = "#00b894" if delta_color == "normal" else "#e17055" if delta_color == "inverse" else "#74b9ff"
            delta_html = f'<p style="color: {color}; margin: 0.5rem 0 0 0; font-size: 0.9rem;">{"+" if delta > 0 else ""}{delta}</p>'
        
        return f"""
        <div class="metric-card">
            <p class="metric-value">{value}</p>
            <p class="metric-label">{label}</p>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def create_status_indicator(text, status_type="info"):
        """Create a status indicator badge."""
        return f'<span class="status-{status_type}">{text}</span>'
    
    @staticmethod
    def create_section_container(content):
        """Create a styled section container."""
        return f'<div class="section-container">{content}</div>'
    
    @staticmethod
    def create_section_header(title, icon=""):
        """Create a styled section header."""
        return f"""
        <div class="section-header">
            <h3 class="section-title">{icon} {title}</h3>
        </div>
        """
    
    @staticmethod
    def style_plotly_chart(fig, height=400):
        """Apply consistent styling to Plotly charts."""
        fig.update_layout(
            height=height,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter",
            font_color="#2c3e50",
            title_font_size=16,
            title_font_color="#2c3e50",
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_xaxes(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            linecolor='rgba(0,0,0,0.2)',
            linewidth=1
        )
        fig.update_yaxes(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            linecolor='rgba(0,0,0,0.2)',
            linewidth=1
        )
        
        return fig
    
    @staticmethod
    def create_navigation_sidebar():
        """Create a styled navigation sidebar."""
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #2c3e50; margin: 0;">🥛 DairyPredict</h2>
                <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">AI-Powered Forecasting</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation menu
            st.markdown("### 📋 Navigation")
            nav_items = [
                ("📊 Dashboard", "Overview and key metrics"),
                ("📁 Company Data", "Multi-company analysis"),
                ("🤖 Model Training", "Train & evaluate models"),
                ("📈 Forecasting", "Generate predictions"),
                ("📋 Reports", "Export and analyze")
            ]
            
            for item, desc in nav_items:
                st.markdown(f"**{item}**")
                st.markdown(f"<small style='color: #7f8c8d;'>{desc}</small>", unsafe_allow_html=True)
                st.markdown("")
    
    @staticmethod
    def create_progress_indicator(current_step, total_steps, step_names):
        """Create a progress indicator showing current step."""
        progress = current_step / total_steps
        
        st.markdown("### 📍 Progress")
        st.progress(progress)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Current:** {step_names[current_step-1]}")
        with col2:
            st.markdown(f"**Step {current_step} of {total_steps}**")
        
        # Show step indicators
        cols = st.columns(total_steps)
        for i, (col, step_name) in enumerate(zip(cols, step_names)):
            with col:
                if i < current_step:
                    st.markdown(f"✅ {step_name}")
                elif i == current_step:
                    st.markdown(f"🔄 {step_name}")
                else:
                    st.markdown(f"⏳ {step_name}")
    
    @staticmethod
    def create_data_summary_card(df):
        """Create a data summary card."""
        if df is None or df.empty:
            return st.error("No data available")
        
        # Calculate metrics
        total_records = len(df)
        
        if 'Date' in df.columns:
            if df['Date'].dtype == 'object':
                df['Date'] = pd.to_datetime(df['Date'])
            date_range = (df['Date'].max() - df['Date'].min()).days
        else:
            date_range = 0
        
        companies = df['Company'].nunique() if 'Company' in df.columns else 1
        products = df['Product'].nunique() if 'Product' in df.columns else 0
        
        # Create metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(UIComponents.create_metric_card(f"{total_records:,}", "TOTAL RECORDS"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(UIComponents.create_metric_card(f"{date_range}", "DAYS OF DATA"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(UIComponents.create_metric_card(f"{companies}", "COMPANIES"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(UIComponents.create_metric_card(f"{products}", "PRODUCTS"), unsafe_allow_html=True)
    
    @staticmethod
    def create_feature_showcase():
        """Create a feature showcase section."""
        st.markdown(UIComponents.create_section_header("🚀 Key Features"), unsafe_allow_html=True)
        
        features = [
            ("📈 Time Series Forecasting", "Advanced Prophet-based demand prediction", "🔮"),
            ("📊 Interactive Dashboards", "Real-time data visualization and analytics", "📱"),
            ("🎯 Production Optimization", "AI-driven production planning and optimization", "⚡"),
            ("📋 Automated Reporting", "Comprehensive reports and export capabilities", "📄"),
            ("🏢 Multi-Company Analysis", "Compare performance across dairy companies", "🔍"),
            ("🤖 Model Training & Evaluation", "Advanced model training and performance analysis", "📊")
        ]
        
        cols = st.columns(2)
        for i, (title, desc, icon) in enumerate(features):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="padding: 1rem; border-left: 4px solid #667eea; background: #f8f9fa; margin-bottom: 1rem; border-radius: 0 8px 8px 0;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #2c3e50;">{icon} {title}</h4>
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.9rem;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
