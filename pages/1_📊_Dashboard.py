import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from utils.ui_components import UIComponents

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def main():
    # Apply custom CSS
    UIComponents.apply_custom_css()
    
    # Create attractive header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Operations Dashboard</h1>
        <p>Real-time insights into your dairy plant operations and forecasting performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if data is available
    if not st.session_state.get('data_uploaded', False) or st.session_state.df is None:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #ffeaa7, #fab1a0); border-radius: 15px; margin: 2rem 0;">
            <h2 style="color: #2d3436; margin-bottom: 1rem;">📁 No Data Available</h2>
            <p style="color: #636e72; font-size: 1.1rem; margin-bottom: 2rem;">Get started by uploading your historical sales data to unlock powerful insights and forecasting capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Upload Data Now", use_container_width=True):
                st.switch_page("pages/2_📁_Data_Upload.py")
        return
    
    df = st.session_state.df
    
    # Create enhanced key metrics with custom styling
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">📈 Key Performance Indicators</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics row with enhanced cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate metrics
    total_records = len(df)
    if df['Date'].dtype == 'object':
        df['Date'] = pd.to_datetime(df['Date'])
    date_range = (df['Date'].max() - df['Date'].min()).days
    total_products = df['Product'].nunique()
    total_quantity = df['Quantity_Sold'].sum()
    total_revenue = (df['Quantity_Sold'] * df['Unit_Price']).sum()
    
    metrics = [
        {"title": "Total Records", "value": f"{total_records:,}", "icon": "📊", "color": "#667eea"},
        {"title": "Date Range", "value": f"{date_range} days", "icon": "📅", "color": "#764ba2"},
        {"title": "Products", "value": str(total_products), "icon": "🥛", "color": "#00b894"},
        {"title": "Total Quantity", "value": f"{total_quantity:,.0f}", "icon": "📦", "color": "#fdcb6e"},
        {"title": "Total Revenue", "value": f"₹{total_revenue:,.0f}", "icon": "💰", "color": "#e17055"}
    ]
    
    columns = [col1, col2, col3, col4, col5]
    
    for i, (col, metric) in enumerate(zip(columns, metrics)):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {metric['color']}, {metric['color']}CC);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 1rem;
                transition: transform 0.3s ease;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{metric['icon']}</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem;">{metric['value']}</div>
                <div style="font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.5px;">{metric['title']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Charts Section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">📊 Sales Analytics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts row 1 with improved styling
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                📈 <span style="margin-left: 0.5rem;">Sales Trend Over Time</span>
            </h4>
        """, unsafe_allow_html=True)
        
        # Aggregate daily sales
        daily_sales = df.groupby('Date').agg({
            'Quantity_Sold': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        fig = px.line(daily_sales, x='Date', y='Quantity_Sold',
                     title='',
                     labels={'Quantity_Sold': 'Quantity', 'Date': 'Date'})
        
        # Enhanced styling for the chart
        fig.update_traces(
            line=dict(color='#667eea', width=3),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)'
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                🥛 <span style="margin-left: 0.5rem;">Product Distribution</span>
            </h4>
        """, unsafe_allow_html=True)
        
        product_totals = df.groupby('Product')['Quantity_Sold'].sum().reset_index()
        
        # Enhanced pie chart with better colors
        colors = ['#667eea', '#764ba2', '#00b894', '#fdcb6e', '#e17055', '#74b9ff', '#a29bfe']
        
        fig = px.pie(product_totals, values='Quantity_Sold', names='Product',
                    title='', color_discrete_sequence=colors)
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Quantity: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Charts row 2 with enhanced styling
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                💰 <span style="margin-left: 0.5rem;">Revenue by Product</span>
            </h4>
        """, unsafe_allow_html=True)
        
        product_revenue = df.groupby('Product')['Revenue'].sum().reset_index()
        product_revenue = product_revenue.sort_values('Revenue', ascending=True)
        
        fig = px.bar(product_revenue, x='Revenue', y='Product',
                    orientation='h',
                    title='',
                    labels={'Revenue': 'Revenue (₹)', 'Product': 'Product'},
                    color='Revenue',
                    color_continuous_scale='Viridis')
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=False),
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False
        )
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                📊 <span style="margin-left: 0.5rem;">Average Unit Prices</span>
            </h4>
        """, unsafe_allow_html=True)
        
        avg_prices = df.groupby('Product')['Unit_Price'].mean().reset_index()
        
        fig = px.bar(avg_prices, x='Product', y='Unit_Price',
                    title='',
                    labels={'Unit_Price': 'Price (₹)', 'Product': 'Product'},
                    color='Unit_Price',
                    color_continuous_scale='plasma')
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_showscale=False
        )
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Avg Price: ₹%{y:.2f}<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Seasonal analysis
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">🌤️ Seasonal Patterns & Trends</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Add date components
    df_seasonal = df.copy()
    df_seasonal['Month'] = df_seasonal['Date'].dt.month
    df_seasonal['DayOfWeek'] = df_seasonal['Date'].dt.day_name()
    df_seasonal['Quarter'] = df_seasonal['Date'].dt.quarter
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                📅 <span style="margin-left: 0.5rem;">Monthly Sales Pattern</span>
            </h4>
        """, unsafe_allow_html=True)
        
        # Monthly trends
        monthly_data = df_seasonal.groupby(['Month', 'Product'])['Quantity_Sold'].sum().reset_index()
        
        fig = px.line(monthly_data, x='Month', y='Quantity_Sold', color='Product',
                     title='',
                     labels={'Quantity_Sold': 'Quantity', 'Month': 'Month'},
                     color_discrete_sequence=['#667eea', '#764ba2', '#00b894', '#fdcb6e', '#e17055'])
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h4 style="color: #2c3e50; margin-bottom: 1rem; display: flex; align-items: center;">
                📊 <span style="margin-left: 0.5rem;">Weekly Sales Pattern</span>
            </h4>
        """, unsafe_allow_html=True)
        
        # Day of week trends
        dow_data = df_seasonal.groupby(['DayOfWeek', 'Product'])['Quantity_Sold'].mean().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data['DayOfWeek'] = pd.Categorical(dow_data['DayOfWeek'], categories=day_order, ordered=True)
        dow_data = dow_data.sort_values('DayOfWeek')
        
        fig = px.bar(dow_data, x='DayOfWeek', y='Quantity_Sold', color='Product',
                    title='',
                    labels={'Quantity_Sold': 'Avg Quantity', 'DayOfWeek': 'Day of Week'},
                    color_discrete_sequence=['#667eea', '#764ba2', '#00b894', '#fdcb6e', '#e17055'])
        
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif"),
            xaxis=dict(showgrid=False, tickangle=-45),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced Recent performance section
    st.markdown("---")
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">📅 Recent Performance Insights</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get last 30 days of data
    last_date = df['Date'].max()
    start_date = last_date - timedelta(days=30)
    recent_data = df[df['Date'] > start_date]
    
    if len(recent_data) > 0:
        # Enhanced metrics with trend indicators
        col1, col2, col3 = st.columns(3)
        
        # Calculate changes
        recent_quantity = recent_data['Quantity_Sold'].sum()
        prev_quantity = df[(df['Date'] <= start_date) & (df['Date'] > start_date - timedelta(days=30))]['Quantity_Sold'].sum()
        quantity_change = ((recent_quantity - prev_quantity) / prev_quantity * 100) if prev_quantity > 0 else 0
        
        recent_revenue = recent_data['Revenue'].sum()
        prev_revenue = df[(df['Date'] <= start_date) & (df['Date'] > start_date - timedelta(days=30))]['Revenue'].sum()
        revenue_change = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        avg_daily_recent = recent_data.groupby('Date')['Quantity_Sold'].sum().mean()
        avg_daily_prev = df[(df['Date'] <= start_date) & (df['Date'] > start_date - timedelta(days=30))].groupby('Date')['Quantity_Sold'].sum().mean()
        daily_change = ((avg_daily_recent - avg_daily_prev) / avg_daily_prev * 100) if avg_daily_prev > 0 else 0
        
        # Custom metric cards with trend indicators
        metrics_data = [
            {"title": "Recent Quantity (30d)", "value": f"{recent_quantity:,.0f}", "change": quantity_change, "icon": "📦"},
            {"title": "Recent Revenue (30d)", "value": f"₹{recent_revenue:,.0f}", "change": revenue_change, "icon": "💰"},
            {"title": "Avg Daily Sales", "value": f"{avg_daily_recent:.0f}", "change": daily_change, "icon": "📊"}
        ]
        
        for i, (col, metric) in enumerate(zip([col1, col2, col3], metrics_data)):
            with col:
                trend_color = "#00b894" if metric["change"] >= 0 else "#e17055"
                trend_icon = "📈" if metric["change"] >= 0 else "📉"
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    border-left: 4px solid {trend_color};
                    margin-bottom: 1rem;
                ">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.5rem;">{metric['icon']}</span>
                        <span style="color: {trend_color}; font-size: 1.2rem;">{trend_icon}</span>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #2c3e50; margin-bottom: 0.3rem;">{metric['value']}</div>
                    <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">{metric['title']}</div>
                    <div style="color: {trend_color}; font-weight: 600; font-size: 0.9rem;">
                        {metric['change']:+.1f}% vs previous period
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced Product Performance Summary
        st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <h4 style="color: #2c3e50; font-weight: 600; display: flex; align-items: center;">
                📊 <span style="margin-left: 0.5rem;">Product Performance Summary</span>
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        summary_data = []
        for product in df['Product'].unique():
            product_data = df[df['Product'] == product]
            recent_product = recent_data[recent_data['Product'] == product]
            
            total_qty = product_data['Quantity_Sold'].sum()
            recent_qty = recent_product['Quantity_Sold'].sum()
            avg_price = product_data['Unit_Price'].mean()
            recent_avg_price = recent_product['Unit_Price'].mean() if len(recent_product) > 0 else avg_price
            
            summary_data.append({
                'Product': product,
                'Total Sales': f"{total_qty:,.0f}",
                'Recent Sales (30d)': f"{recent_qty:,.0f}",
                'Avg Price': f"₹{avg_price:.2f}",
                'Recent Avg Price': f"₹{recent_avg_price:.2f}",
                'Market Share': f"{(total_qty / df['Quantity_Sold'].sum() * 100):.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Style the dataframe
        st.markdown("""
        <style>
        .dataframe {
            border: none !important;
        }
        .dataframe th {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px !important;
            border: none !important;
        }
        .dataframe td {
            padding: 10px !important;
            border-bottom: 1px solid #e1e5e9 !important;
        }
        .dataframe tbody tr:hover {
            background-color: #f8f9fa !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(summary_df, use_container_width=True)
    
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;">
            <h4 style="color: #6c757d;">📊 No Recent Data Available</h4>
            <p style="color: #6c757d;">No data found for the last 30 days.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Model status section
    if st.session_state.get('models_trained', False):
        st.markdown("---")
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">🤖 AI Model Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #00b894, #00a085);
                padding: 1.5rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,184,148,0.3);
            ">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">✅</div>
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">Models Ready</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">AI models are trained and operational</div>
            </div>
            """, unsafe_allow_html=True)
            
            if 'forecasts' in st.session_state and st.session_state.forecasts:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #74b9ff, #0984e3);
                    padding: 1rem;
                    border-radius: 10px;
                    color: white;
                    text-align: center;
                    margin-top: 1rem;
                    box-shadow: 0 4px 15px rgba(116,185,255,0.3);
                ">
                    <div style="font-size: 1.1rem; font-weight: 600;">📊 Forecasts Available</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">Ready for {len(st.session_state.forecasts)} products</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: 2px solid #e1e5e9;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 1rem;">Evaluate Models</div>
            """, unsafe_allow_html=True)
            
            if st.button("📊 Check Performance", use_container_width=True, help="Analyze model accuracy and performance metrics"):
                st.switch_page("pages/3_🤖_Model_Training.py")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border: 2px solid #e1e5e9;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔄</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 1rem;">Update Forecasts</div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Generate New Forecasts", use_container_width=True, help="Generate fresh forecasts with current models"):
                st.switch_page("pages/4_📈_Forecasting.py")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("---")
        st.markdown("""
        <div style="margin: 2rem 0;">
            <h3 style="color: #2c3e50; font-weight: 600; margin-bottom: 1.5rem;">🤖 AI Model Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffeaa7, #fab1a0);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: #2d3436;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <div style="font-size: 1.4rem; font-weight: 600; margin-bottom: 1rem;">Ready to Train Models?</div>
            <div style="font-size: 1rem; margin-bottom: 2rem; opacity: 0.8;">Train AI models to unlock powerful forecasting capabilities and optimize your dairy operations.</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Model Training", use_container_width=True):
                st.switch_page("pages/3_🤖_Model_Training.py")

if __name__ == "__main__":
    main()
