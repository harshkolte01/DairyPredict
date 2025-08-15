import streamlit as st
import pandas as pd
import numpy as np
from utils.forecasting import DairyForecaster
from utils.optimization import ProductionOptimizer
from utils.gemini_analyzer import GeminiAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import io
import re

st.set_page_config(page_title="Reports", page_icon="📋", layout="wide")

def safe_color_to_rgba(color, alpha=0.2):
    """Safely convert color to RGBA format."""
    try:
        # If it's already in RGB format like 'rgb(255, 0, 0)'
        if color.startswith('rgb('):
            # Extract RGB values
            rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color)
            if rgb_match:
                r, g, b = rgb_match.groups()
                return f'rgba({r},{g},{b},{alpha})'
        
        # If it's a hex color
        if color.startswith('#'):
            rgb = px.colors.hex_to_rgb(color)
            return f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha})'
        
        # Fallback to a default color
        return f'rgba(70,130,180,{alpha})'
    except:
        # If all else fails, use a safe default
        return f'rgba(70,130,180,{alpha})'

def main():
    st.title("📋 Reports & Analytics")
    st.markdown("Comprehensive reports and analysis for dairy plant operations")
    
    # Check data availability
    if not st.session_state.get('data_uploaded', False) or st.session_state.df is None:
        st.warning("📁 No data available. Please upload data first.")
        if st.button("📁 Upload Data"):
            st.switch_page("pages/2_📁_Data_Upload.py")
        return
    
    df = st.session_state.df
    
    # Report type selection
    st.subheader("📊 Select Report Type")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Historical Analysis", use_container_width=True):
            st.session_state.report_type = "historical"
    
    with col2:
        if st.button("🔮 Forecast Analysis", use_container_width=True):
            if st.session_state.get('forecasts'):
                st.session_state.report_type = "forecast"
            else:
                st.error("No forecasts available. Generate forecasts first.")
                return
    
    with col3:
        if st.button("🏭 Production Report", use_container_width=True):
            if st.session_state.get('forecasts'):
                st.session_state.report_type = "production"
            else:
                st.error("No forecasts available. Generate forecasts first.")
                return
    
    with col4:
        if st.button("🤖 AI Executive Report", use_container_width=True):
            if st.session_state.get('forecasts'):
                st.session_state.report_type = "ai_executive"
            else:
                st.error("No forecasts available. Generate forecasts first.")
                return
    
    # Initialize report type if not set
    if 'report_type' not in st.session_state:
        st.session_state.report_type = "historical"
    
    report_type = st.session_state.report_type
    
    st.markdown("---")
    
    # Report generation based on type
    if report_type == "historical":
        generate_historical_report(df)
    elif report_type == "forecast" and st.session_state.get('forecasts'):
        generate_forecast_report(df, st.session_state.forecasts)
    elif report_type == "production" and st.session_state.get('forecasts'):
        generate_production_report(df, st.session_state.forecasts)
    elif report_type == "ai_executive" and st.session_state.get('forecasts'):
        generate_ai_executive_report(df, st.session_state.forecasts)
    
    # Export section
    st.markdown("---")
    generate_export_section(df, report_type)

def generate_historical_report(df):
    """Generate historical sales analysis report."""
    st.subheader("📈 Historical Sales Analysis Report")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=df['Date'].min(),
            min_value=df['Date'].min(),
            max_value=df['Date'].max()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=df['Date'].max(),
            min_value=df['Date'].min(),
            max_value=df['Date'].max()
        )
    
    # Filter data
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    if len(filtered_df) == 0:
        st.warning("No data available for selected date range.")
        return
    
    # Executive Summary
    st.subheader("📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_df['Revenue'].sum()
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    
    with col2:
        total_quantity = filtered_df['Quantity_Sold'].sum()
        st.metric("Total Quantity Sold", f"{total_quantity:,.0f}")
    
    with col3:
        avg_daily_sales = filtered_df.groupby('Date')['Quantity_Sold'].sum().mean()
        st.metric("Avg Daily Sales", f"{avg_daily_sales:.0f}")
    
    with col4:
        num_products = filtered_df['Product'].nunique()
        st.metric("Active Products", num_products)
    
    # Performance by Product
    st.subheader("🥛 Product Performance Analysis")
    
    product_performance = filtered_df.groupby('Product').agg({
        'Quantity_Sold': ['sum', 'mean', 'std'],
        'Revenue': ['sum', 'mean'],
        'Unit_Price': 'mean'
    }).round(2)
    
    product_performance.columns = ['Total_Qty', 'Avg_Daily_Qty', 'Qty_StdDev', 'Total_Revenue', 'Avg_Daily_Revenue', 'Avg_Unit_Price']
    product_performance['Market_Share_Qty'] = (product_performance['Total_Qty'] / product_performance['Total_Qty'].sum() * 100).round(1)
    product_performance['Market_Share_Revenue'] = (product_performance['Total_Revenue'] / product_performance['Total_Revenue'].sum() * 100).round(1)
    
    st.dataframe(product_performance, use_container_width=True)
    
    # Trend Analysis
    st.subheader("📈 Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily sales trend
        daily_sales = filtered_df.groupby('Date')['Quantity_Sold'].sum().reset_index()
        fig = px.line(daily_sales, x='Date', y='Quantity_Sold',
                     title='Daily Sales Trend',
                     labels={'Quantity_Sold': 'Quantity', 'Date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product mix over time
        monthly_product_sales = filtered_df.groupby([filtered_df['Date'].dt.to_period('M'), 'Product'])['Quantity_Sold'].sum().reset_index()
        monthly_product_sales['Date'] = monthly_product_sales['Date'].astype(str)
        
        fig = px.area(monthly_product_sales, x='Date', y='Quantity_Sold', color='Product',
                     title='Monthly Product Mix')
        st.plotly_chart(fig, use_container_width=True)
    
    # Seasonality Analysis
    st.subheader("🌤️ Seasonality Analysis")
    
    seasonal_df = filtered_df.copy()
    seasonal_df['Month'] = seasonal_df['Date'].dt.month
    seasonal_df['DayOfWeek'] = seasonal_df['Date'].dt.day_name()
    seasonal_df['Quarter'] = seasonal_df['Date'].dt.quarter
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly seasonality
        monthly_avg = seasonal_df.groupby(['Month', 'Product'])['Quantity_Sold'].mean().reset_index()
        fig = px.line(monthly_avg, x='Month', y='Quantity_Sold', color='Product',
                     title='Monthly Seasonality Pattern')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Day of week pattern
        dow_avg = seasonal_df.groupby(['DayOfWeek', 'Product'])['Quantity_Sold'].mean().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_avg['DayOfWeek'] = pd.Categorical(dow_avg['DayOfWeek'], categories=day_order, ordered=True)
        dow_avg = dow_avg.sort_values('DayOfWeek')
        
        fig = px.bar(dow_avg, x='DayOfWeek', y='Quantity_Sold', color='Product',
                    title='Day of Week Sales Pattern')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Key Insights
    st.subheader("🎯 Key Insights")
    
    insights = generate_historical_insights(filtered_df)
    
    for insight in insights:
        st.info(f"📌 {insight}")

def generate_forecast_report(df, forecasts):
    """Generate forecast analysis report."""
    st.subheader("🔮 Demand Forecast Analysis Report")
    
    # Forecast overview
    st.subheader("📊 Forecast Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Products Forecasted", len(forecasts))
    
    with col2:
        # Calculate total forecasted demand (next 30 days)
        total_forecast = 0
        for product, forecast in forecasts.items():
            future_30 = forecast.tail(30)
            total_forecast += future_30['yhat'].sum()
        st.metric("30-Day Forecast", f"{total_forecast:.0f}")
    
    with col3:
        # Get forecast date range
        if forecasts:
            sample_forecast = list(forecasts.values())[0]
            forecast_days = len(sample_forecast.tail(30))
            st.metric("Forecast Horizon", f"{forecast_days} days")
    
    # Forecast comparison with historical
    st.subheader("📈 Forecast vs Historical Comparison")
    
    comparison_data = []
    for product in forecasts.keys():
        forecast = forecasts[product]
        historical_avg = df[df['Product'] == product].groupby('Date')['Quantity_Sold'].mean().mean()
        
        future_forecast = forecast.tail(30)
        forecast_avg = future_forecast['yhat'].mean()
        
        comparison_data.append({
            'Product': product,
            'Historical_Avg': historical_avg,
            'Forecast_Avg': forecast_avg,
            'Change_%': ((forecast_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0,
            'Confidence_Width': (future_forecast['yhat_upper'] - future_forecast['yhat_lower']).mean()
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df.round(2), use_container_width=True)
    
    # Forecast visualizations
    st.subheader("📊 Forecast Visualizations")
    
    # Calculate appropriate vertical spacing based on number of subplots
    num_plots = len(forecasts)
    
    # Handle large number of products differently
    MAX_PLOTS = 15  # Maximum number of plots for readable visualization
    if num_plots > MAX_PLOTS:
        st.warning(f"⚠️ Large number of products ({num_plots}). Showing top {MAX_PLOTS} products by forecasted demand for better visualization.")
        st.info("💡 Complete forecast data for all products is available in the summary table above.")
        
        # Calculate average forecasted demand for each product
        product_demands = []
        for product, forecast in forecasts.items():
            avg_demand = forecast['yhat'].mean()
            product_demands.append((product, avg_demand, forecast))
        
        # Sort by demand and take top products
        product_demands.sort(key=lambda x: x[1], reverse=True)
        top_forecasts = {product: forecast for product, _, forecast in product_demands[:MAX_PLOTS]}
        forecasts_to_plot = top_forecasts
        num_plots = len(forecasts_to_plot)
    else:
        forecasts_to_plot = forecasts
    
    if num_plots > 1:
        max_spacing = 1 / (num_plots - 1)
        vertical_spacing = min(0.1, max_spacing * 0.8)  # Use 80% of max allowed spacing
    else:
        vertical_spacing = 0.1
    
    # Create combined forecast chart
    fig = make_subplots(
        rows=num_plots, cols=1,
        subplot_titles=list(forecasts_to_plot.keys()),
        vertical_spacing=vertical_spacing
    )
    
    for i, (product, forecast) in enumerate(forecasts_to_plot.items()):
        future_data = forecast.tail(30)
        
        fig.add_trace(
            go.Scatter(
                x=future_data['ds'],
                y=future_data['yhat'],
                mode='lines',
                name=f'{product} Forecast',
                line=dict(color=px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)])
            ),
            row=i+1, col=1
        )
        
        # Add confidence interval
        color = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
        fill_color = safe_color_to_rgba(color, 0.2)
        
        fig.add_trace(
            go.Scatter(
                x=future_data['ds'].tolist() + future_data['ds'].tolist()[::-1],
                y=future_data['yhat_upper'].tolist() + future_data['yhat_lower'].tolist()[::-1],
                fill='toself',
                fillcolor=fill_color,
                line=dict(color='rgba(255,255,255,0)'),
                name=f'{product} Confidence',
                showlegend=False
            ),
            row=i+1, col=1
        )
    
    fig.update_layout(height=300*len(forecasts_to_plot), title_text="30-Day Demand Forecasts")
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast accuracy metrics (if available)
    if hasattr(st.session_state, 'forecaster') and st.session_state.forecaster.model_performance:
        st.subheader("🎯 Model Performance Metrics")
        
        performance_data = []
        for product, performance in st.session_state.forecaster.model_performance.items():
            if performance and product in forecasts:
                performance_data.append({
                    'Product': product,
                    'MAE': performance.get('mae', 0),
                    'RMSE': performance.get('rmse', 0),
                    'MAPE_%': performance.get('mape', 0),
                    'Status': performance.get('note', 'OK')
                })
        
        if performance_data:
            perf_df = pd.DataFrame(performance_data)
            st.dataframe(perf_df.round(2), use_container_width=True)

def generate_production_report(df, forecasts):
    """Generate production optimization report."""
    st.subheader("🏭 Production Optimization Report")
    
    # Initialize optimizer
    optimizer = ProductionOptimizer()
    
    # Production configuration
    st.subheader("⚙️ Production Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        safety_stock = st.slider("Safety Stock %", 0, 50, 15) / 100
        forecast_horizon = st.selectbox("Planning Horizon (days)", [7, 14, 30], index=2)
    
    with col2:
        st.write("**Production Capacities:**")
        capacities = {}
        for product in forecasts.keys():
            default_cap = optimizer.default_capacities.get(product, 1000)
            capacities[product] = st.number_input(
                f"{product} (units/day)",
                min_value=100,
                value=default_cap,
                key=f"prod_cap_{product}"
            )
    
    # Generate optimization analysis
    if st.button("🚀 Generate Production Analysis"):
        # Prepare forecast data
        all_forecasts = []
        for product, forecast in forecasts.items():
            forecast_data = forecast.tail(forecast_horizon).copy()
            forecast_data['product'] = product
            forecast_data = forecast_data.rename(columns={
                'ds': 'date',
                'yhat': 'predicted_demand'
            })
            all_forecasts.append(forecast_data[['date', 'product', 'predicted_demand']])
        
        combined_forecasts = pd.concat(all_forecasts, ignore_index=True)
        
        # Generate comprehensive optimization summary
        optimization_summary = optimizer.generate_optimization_summary(
            combined_forecasts, 
            list(forecasts.keys()), 
            forecast_horizon
        )
        
        # Display optimization results
        st.subheader("📊 Production Optimization Results")
        
        # Overall metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_cost = optimization_summary['overall_metrics']['total_production_cost']
            st.metric("Total Production Cost", f"₹{total_cost:,.0f}")
        
        with col2:
            total_revenue = optimization_summary['overall_metrics']['total_potential_revenue']
            st.metric("Potential Revenue", f"₹{total_revenue:,.0f}")
        
        with col3:
            profit_margin = optimization_summary['overall_metrics']['overall_profit_margin']
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        
        # Product-wise analysis
        st.subheader("🥛 Product-wise Production Analysis")
        
        production_analysis = []
        for product, analysis in optimization_summary['products_analysis'].items():
            production_analysis.append({
                'Product': product,
                'Forecasted_Demand': f"{analysis['total_forecasted_demand']:.0f}",
                'Optimal_Production': f"{analysis['total_optimal_production']:.0f}",
                'Capacity_Utilization_%': f"{analysis['avg_capacity_utilization']:.1f}",
                'Production_Cost': f"₹{analysis['total_production_cost']:,.0f}",
                'Potential_Revenue': f"₹{analysis['total_potential_revenue']:,.0f}",
                'Profit_Margin_%': f"{analysis['avg_profit_margin']:.1f}"
            })
        
        prod_analysis_df = pd.DataFrame(production_analysis)
        st.dataframe(prod_analysis_df, use_container_width=True)
        
        # Capacity utilization chart
        st.subheader("📊 Capacity Utilization Analysis")
        
        utilization_data = []
        for product, analysis in optimization_summary['products_analysis'].items():
            utilization_data.append({
                'Product': product,
                'Utilization': analysis['avg_capacity_utilization'],
                'Capacity': capacities.get(product, 1000)
            })
        
        util_df = pd.DataFrame(utilization_data)
        
        fig = px.bar(util_df, x='Product', y='Utilization',
                    title='Average Capacity Utilization by Product',
                    labels={'Utilization': 'Utilization %'})
        
        # Add reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="green", 
                     annotation_text="Optimal Min (70%)")
        fig.add_hline(y=85, line_dash="dash", line_color="orange", 
                     annotation_text="Optimal Max (85%)")
        fig.add_hline(y=100, line_dash="dash", line_color="red", 
                     annotation_text="Full Capacity")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Production Recommendations")
        
        for product, analysis in optimization_summary['products_analysis'].items():
            st.write(f"**{product}:**")
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    st.info(f"• {rec}")
            else:
                st.success("• Production parameters are optimal")
        
        # Store optimization results
        st.session_state.optimization_results = optimization_summary

def generate_export_section(df, report_type):
    """Generate export options for reports."""
    st.subheader("📁 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export raw data as CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📊 Export Data (CSV)",
            csv_data,
            file_name=f"dairy_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export forecast data (if available)
        if st.session_state.get('forecasts') and report_type in ['forecast', 'production']:
            forecast_export = []
            for product, forecast in st.session_state.forecasts.items():
                forecast_data = forecast.tail(30).copy()
                forecast_data['Product'] = product
                forecast_export.append(forecast_data[['ds', 'Product', 'yhat', 'yhat_lower', 'yhat_upper']])
            
            if forecast_export:
                combined_forecast = pd.concat(forecast_export, ignore_index=True)
                combined_forecast = combined_forecast.rename(columns={
                    'ds': 'Date',
                    'yhat': 'Predicted_Demand',
                    'yhat_lower': 'Lower_Bound',
                    'yhat_upper': 'Upper_Bound'
                })
                
                forecast_csv = combined_forecast.to_csv(index=False)
                st.download_button(
                    "🔮 Export Forecasts (CSV)",
                    forecast_csv,
                    file_name=f"forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("🔮 Export Forecasts", disabled=True, use_container_width=True)
    
    with col3:
        # Export summary report
        if st.button("📄 Generate Summary Report", use_container_width=True):
            summary = generate_summary_report(df, report_type)
            
            st.download_button(
                "📄 Download Summary (TXT)",
                summary,
                file_name=f"summary_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def generate_historical_insights(df):
    """Generate insights from historical data."""
    insights = []
    
    # Product performance insights
    product_totals = df.groupby('Product')['Quantity_Sold'].sum()
    top_product = product_totals.idxmax()
    top_product_share = (product_totals.max() / product_totals.sum() * 100)
    insights.append(f"{top_product} is the top-selling product with {top_product_share:.1f}% market share")
    
    # Trend insights
    daily_sales = df.groupby('Date')['Quantity_Sold'].sum()
    recent_trend = daily_sales.tail(7).mean() - daily_sales.head(7).mean()
    if recent_trend > 0:
        insights.append(f"Sales show an increasing trend with recent weekly average {recent_trend:.0f} units higher than initial period")
    else:
        insights.append(f"Sales show a decreasing trend with recent weekly average {abs(recent_trend):.0f} units lower than initial period")
    
    # Seasonal insights
    monthly_sales = df.groupby(df['Date'].dt.month)['Quantity_Sold'].sum()
    peak_month = monthly_sales.idxmax()
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                   7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    insights.append(f"Peak sales month is {month_names.get(peak_month, peak_month)} indicating seasonal demand patterns")
    
    # Price insights
    avg_prices = df.groupby('Product')['Unit_Price'].mean()
    revenue_per_unit = df.groupby('Product')['Revenue'].sum() / df.groupby('Product')['Quantity_Sold'].sum()
    premium_product = revenue_per_unit.idxmax()
    insights.append(f"{premium_product} generates highest revenue per unit, indicating premium positioning opportunity")
    
    return insights

def generate_summary_report(df, report_type):
    """Generate a text summary report."""
    report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    summary = f"""
DAIRY PLANT DEMAND FORECASTING SYSTEM
SUMMARY REPORT - {report_type.upper()}
Generated on: {report_date}

{'='*50}

DATA OVERVIEW:
- Total Records: {len(df):,}
- Date Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}
- Products: {', '.join(df['Product'].unique())}
- Total Quantity Sold: {df['Quantity_Sold'].sum():,.0f}
- Total Revenue: ₹{df['Revenue'].sum():,.0f}

PRODUCT PERFORMANCE:
"""
    
    for product in df['Product'].unique():
        product_data = df[df['Product'] == product]
        summary += f"""
{product}:
- Total Sales: {product_data['Quantity_Sold'].sum():,.0f} units
- Total Revenue: ₹{product_data['Revenue'].sum():,.0f}
- Average Price: ₹{product_data['Unit_Price'].mean():.2f}
- Market Share: {(product_data['Quantity_Sold'].sum() / df['Quantity_Sold'].sum() * 100):.1f}%
"""
    
    if report_type == "forecast" and st.session_state.get('forecasts'):
        summary += f"""
{'='*50}

FORECAST SUMMARY:
"""
        for product, forecast in st.session_state.forecasts.items():
            future_30 = forecast.tail(30)
            summary += f"""
{product} (Next 30 Days):
- Predicted Total Demand: {future_30['yhat'].sum():.0f}
- Average Daily Demand: {future_30['yhat'].mean():.0f}
- Confidence Range: {future_30['yhat_lower'].sum():.0f} - {future_30['yhat_upper'].sum():.0f}
"""
    
    summary += f"""
{'='*50}

Report generated by Dairy Plant Demand Forecasting System
For questions or support, please contact your system administrator.
"""
    
    return summary

def generate_ai_executive_report(df, forecasts):
    """Generate AI-powered executive summary report."""
    st.subheader("🤖 AI Executive Summary Report")
    
    # Initialize Gemini analyzer
    gemini_analyzer = GeminiAnalyzer()
    
    # Prepare performance metrics
    performance_metrics = {
        'total_revenue': float(df['Revenue'].sum()),
        'total_volume': float(df['Quantity_Sold'].sum()),
        'product_count': int(df['Product'].nunique()),
        'company_count': int(df['Company'].nunique()),
        'time_span_days': int((df['Date'].max() - df['Date'].min()).days),
        'avg_daily_revenue': float(df.groupby('Date')['Revenue'].sum().mean()),
        'top_product': df.groupby('Product')['Revenue'].sum().idxmax(),
        'growth_trend': 'positive' if df['Revenue'].iloc[-100:].mean() > df['Revenue'].iloc[:100].mean() else 'negative'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Executive Summary", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your business data and generating executive insights..."):
                executive_summary = gemini_analyzer.generate_executive_summary(forecasts, performance_metrics)
                
                if executive_summary and "Error" not in executive_summary:
                    st.markdown("#### 📋 Executive Summary")
                    st.markdown(executive_summary)
                    
                    # Store summary for export
                    st.session_state.ai_executive_summary = executive_summary
                else:
                    st.error("Unable to generate AI executive summary. Please check your API key configuration.")
    
    with col2:
        if st.button("📊 Business Intelligence Dashboard", type="secondary", use_container_width=True):
            # Create comprehensive business metrics
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Total Revenue", f"₹{performance_metrics['total_revenue']:,.0f}")
                st.metric("Product Portfolio", f"{performance_metrics['product_count']} products")
            
            with col_b:
                st.metric("Total Volume", f"{performance_metrics['total_volume']:,.0f} units")
                st.metric("Market Presence", f"{performance_metrics['company_count']} companies")
            
            with col_c:
                st.metric("Data Coverage", f"{performance_metrics['time_span_days']} days")
                st.metric("Daily Avg Revenue", f"₹{performance_metrics['avg_daily_revenue']:,.0f}")
    
    # Show forecast performance metrics if available
    if forecasts:
        st.markdown("#### 🎯 Forecast Performance Metrics")
        
        forecast_metrics = []
        for product, forecast_data in forecasts.items():
            if hasattr(forecast_data, 'tail'):
                recent_forecast = forecast_data.tail(30)
                forecast_metrics.append({
                    'Product': product,
                    'Avg_Forecast': f"{recent_forecast['yhat'].mean():.0f}",
                    'Peak_Demand': f"{recent_forecast['yhat'].max():.0f}",
                    'Confidence_Width': f"{(recent_forecast['yhat_upper'] - recent_forecast['yhat_lower']).mean():.0f}",
                    'Trend': 'Increasing' if recent_forecast['yhat'].iloc[-1] > recent_forecast['yhat'].iloc[0] else 'Decreasing'
                })
        
        if forecast_metrics:
            metrics_df = pd.DataFrame(forecast_metrics)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # AI analysis of forecast performance
            if st.button("🔍 AI Analysis of Forecast Trends", use_container_width=True):
                with st.spinner("🤖 Analyzing forecast patterns..."):
                    forecast_insights = gemini_analyzer.analyze_forecast_data(forecasts)
                    
                    if forecast_insights:
                        st.markdown("#### 🎯 AI Forecast Analysis")
                        
                        col_x, col_y = st.columns(2)
                        
                        with col_x:
                            if forecast_insights.key_trends:
                                st.markdown("**📈 Key Trends:**")
                                for trend in forecast_insights.key_trends:
                                    st.write(f"• {trend}")
                            
                            if forecast_insights.opportunities:
                                st.markdown("**🚀 Opportunities:**")
                                for opp in forecast_insights.opportunities:
                                    st.success(f"• {opp}")
                        
                        with col_y:
                            if forecast_insights.business_recommendations:
                                st.markdown("**💡 Recommendations:**")
                                for rec in forecast_insights.business_recommendations:
                                    st.write(f"• {rec}")
                            
                            if forecast_insights.risk_factors:
                                st.markdown("**⚠️ Risk Factors:**")
                                for risk in forecast_insights.risk_factors:
                                    st.warning(f"• {risk}")
                        
                        st.markdown(f"**🎯 AI Confidence: {forecast_insights.confidence_score:.1%}**")
                    
                    else:
                        st.error("Unable to generate forecast analysis.")
    
    # Export AI report
    st.markdown("---")
    st.subheader("📁 Export AI Report")
    
    if hasattr(st.session_state, 'ai_executive_summary'):
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # Download AI summary as text
            ai_report_text = f"""
AI EXECUTIVE SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{st.session_state.ai_executive_summary}

BUSINESS METRICS SUMMARY:
- Total Revenue: ₹{performance_metrics['total_revenue']:,.0f}
- Total Volume: {performance_metrics['total_volume']:,.0f} units
- Product Portfolio: {performance_metrics['product_count']} products
- Data Coverage: {performance_metrics['time_span_days']} days
- Top Performing Product: {performance_metrics['top_product']}
- Business Trend: {performance_metrics['growth_trend']}

Report generated by AI-Powered Dairy Forecasting System
"""
            
            st.download_button(
                "📄 Download AI Summary",
                ai_report_text,
                file_name=f"ai_executive_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_export2:
            if st.button("📧 Email Report (Coming Soon)", use_container_width=True):
                st.info("Email functionality will be available in the next update!")
    else:
        st.info("Generate an AI executive summary first to enable export options.")

if __name__ == "__main__":
    main()
