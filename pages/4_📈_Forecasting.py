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
import time

st.set_page_config(page_title="Forecasting", page_icon="📈", layout="wide")

def main():
    st.title("📈 Demand Forecasting")
    st.markdown("Generate AI-powered demand forecasts and production recommendations")
    
    # Check if models are trained
    if not st.session_state.get('models_trained', False) or 'forecaster' not in st.session_state:
        st.warning("🤖 No trained models available. Please train models first.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Train Models"):
                st.switch_page("pages/3_🤖_Model_Training.py")
        with col2:
            if st.button("📊 View Dashboard"):
                st.switch_page("pages/1_📊_Dashboard.py")
        return
    
    forecaster = st.session_state.forecaster
    
    # Initialize optimizer
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = ProductionOptimizer()
    
    optimizer = st.session_state.optimizer
    
    # Initialize forecasts dict if not exists
    if 'forecasts' not in st.session_state:
        st.session_state.forecasts = {}
    
    # Forecasting configuration
    st.subheader("⚙️ Forecast Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Select products
        available_products = list(forecaster.models.keys())
        selected_products = st.multiselect(
            "Select Products",
            available_products,
            default=available_products,
            help="Choose products to forecast"
        )
    
    with col2:
        # Forecast horizon
        forecast_horizon = st.selectbox(
            "Forecast Horizon",
            [7, 14, 30, 60, 90],
            index=2,
            help="Number of days to forecast"
        )
    
    with col3:
        # Include historical data in visualization
        include_history = st.checkbox(
            "Include Historical Data",
            value=True,
            help="Show historical data alongside forecasts"
        )
    
    # Generate forecasts section
    st.markdown("---")
    st.subheader("🔮 Generate Forecasts")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate Forecasts", type="primary", use_container_width=True, disabled=not selected_products):
            if not selected_products:
                st.error("❌ Please select at least one product")
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            forecasts = {}
            
            for i, product in enumerate(selected_products):
                status_text.text(f"Generating forecast for {product}...")
                progress_bar.progress(i / len(selected_products))
                
                # Generate forecast
                forecast, message = forecaster.generate_forecast(
                    product, 
                    forecast_horizon, 
                    include_history=include_history
                )
                
                if forecast is not None:
                    forecasts[product] = forecast
                    st.session_state.forecasts[product] = forecast
                
                progress_bar.progress((i + 1) / len(selected_products))
                time.sleep(0.3)
            
            status_text.text("Forecasts generated!")
            st.session_state.current_forecasts = forecasts
            st.success(f"✅ Generated forecasts for {len(forecasts)} product(s)")
            time.sleep(1)
            st.rerun()
    
    # Display forecasts
    if 'current_forecasts' in st.session_state and st.session_state.current_forecasts:
        forecasts = st.session_state.current_forecasts
        
        st.markdown("---")
        st.subheader("📊 Forecast Results")
        
        # Add company comparison section
        if st.session_state.get('data_uploaded', False) and st.session_state.df is not None:
            df = st.session_state.df
            if 'Company' in df.columns and len(df['Company'].unique()) > 1:
                # Create tabs for individual forecasts vs company comparison
                tab1, tab2 = st.tabs(["📈 Individual Forecasts", "🏢 Company Comparison"])
                
                with tab2:
                    st.markdown("### 🔍 Dairy Company Demand Comparison")
                    st.markdown("**Compare forecasted demand across all dairy companies by product**")
                    
                    # Get unique companies
                    companies = df['Company'].unique()
                    
                    # Create comprehensive comparison for each product
                    for product in selected_products:
                        if product in forecasts:
                            st.markdown(f"#### 🥛 {product} - Market Analysis")
                            
                            # Generate forecasts for each company
                            company_forecasts = {}
                            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                            
                            # Create comparison chart
                            fig_comparison = go.Figure()
                            
                            for i, company in enumerate(companies):
                                # Filter data for this company and product
                                company_data = df[(df['Company'] == company) & (df['Product'] == product)]
                                
                                if len(company_data) > 10:  # Ensure sufficient data
                                    # Generate quick forecast for comparison
                                    from utils.data_processor import DataProcessor
                                    prophet_data = DataProcessor.prepare_prophet_data(company_data, product)
                                    
                                    if len(prophet_data) > 20:  # Minimum data requirement
                                        # Create temporary forecaster
                                        temp_forecaster = DairyForecaster()
                                        success, _ = temp_forecaster.train_model(prophet_data, f"{company}_{product}")
                                        
                                        if success:
                                            company_forecast, _ = temp_forecaster.generate_forecast(
                                                f"{company}_{product}", 
                                                forecast_horizon, 
                                                include_history=False
                                            )
                                            
                                            if company_forecast is not None:
                                                company_forecasts[company] = company_forecast
                                                
                                                # Add to comparison chart
                                                fig_comparison.add_trace(go.Scatter(
                                                    x=company_forecast['ds'],
                                                    y=company_forecast['yhat'],
                                                    mode='lines+markers',
                                                    name=f"{company}",
                                                    line=dict(color=colors[i % len(colors)], width=3),
                                                    marker=dict(size=6)
                                                ))
                            
                            if len(company_forecasts) > 1:
                                fig_comparison.update_layout(
                                    title=f'{product} - Demand Forecast Comparison Across Companies',
                                    xaxis_title='Date',
                                    yaxis_title='Predicted Demand (Units)',
                                    hovermode='x unified',
                                    height=500,
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                    template="plotly_white"
                                )
                                
                                st.plotly_chart(fig_comparison, use_container_width=True)
                                
                                # Comprehensive comparison metrics
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.markdown("**🏆 Total Forecasted Demand Rankings**")
                                    company_totals = []
                                    for company, forecast in company_forecasts.items():
                                        total_demand = forecast['yhat'].sum()
                                        company_totals.append((company, total_demand))
                                    
                                    company_totals.sort(key=lambda x: x[1], reverse=True)
                                    
                                    for rank, (company, total) in enumerate(company_totals, 1):
                                        if rank == 1:
                                            st.success(f"🥇 **{company}**: {total:,.0f} units")
                                        elif rank == 2:
                                            st.info(f"🥈 **{company}**: {total:,.0f} units")
                                        else:
                                            st.write(f"🥉 **{company}**: {total:,.0f} units")
                                
                                with col2:
                                    st.markdown("**📊 Average Daily Demand**")
                                    company_averages = []
                                    for company, forecast in company_forecasts.items():
                                        avg_demand = forecast['yhat'].mean()
                                        company_averages.append((company, avg_demand))
                                    
                                    company_averages.sort(key=lambda x: x[1], reverse=True)
                                    
                                    for rank, (company, avg) in enumerate(company_averages, 1):
                                        icon = "📈" if rank == 1 else "📊"
                                        color = "success" if rank == 1 else "write"
                                        method = st.success if rank == 1 else st.write
                                        method(f"{icon} **{company}**: {avg:,.0f} units/day")
                                
                                with col3:
                                    st.markdown("**⚡ Peak Demand Analysis**")
                                    company_peaks = []
                                    for company, forecast in company_forecasts.items():
                                        peak_demand = forecast['yhat'].max()
                                        peak_date = forecast.loc[forecast['yhat'].idxmax(), 'ds'].strftime('%Y-%m-%d')
                                        company_peaks.append((company, peak_demand, peak_date))
                                    
                                    company_peaks.sort(key=lambda x: x[1], reverse=True)
                                    
                                    for rank, (company, peak, date) in enumerate(company_peaks, 1):
                                        icon = "⚡" if rank == 1 else "📊"
                                        method = st.success if rank == 1 else st.write
                                        method(f"{icon} **{company}**: {peak:,.0f} units")
                                        st.caption(f"Peak on: {date}")
                                
                                # Market share visualization and analysis
                                st.markdown("**🎯 Market Share Analysis**")
                                total_market = sum(forecast['yhat'].sum() for forecast in company_forecasts.values())
                                
                                market_data = []
                                for company, forecast in company_forecasts.items():
                                    company_total = forecast['yhat'].sum()
                                    market_share = (company_total / total_market) * 100
                                    growth_rate = ((forecast['yhat'].iloc[-7:].mean() - forecast['yhat'].iloc[:7].mean()) / forecast['yhat'].iloc[:7].mean()) * 100
                                    market_data.append({
                                        'Company': company, 
                                        'Market Share (%)': market_share, 
                                        'Total Demand': company_total,
                                        'Growth Rate (%)': growth_rate
                                    })
                                
                                market_df = pd.DataFrame(market_data)
                                market_df = market_df.sort_values('Market Share (%)', ascending=False)
                                
                                # Market share pie chart and growth analysis
                                col1, col2 = st.columns([1, 1])
                                
                                with col1:
                                    fig_pie = px.pie(
                                        market_df, 
                                        values='Market Share (%)', 
                                        names='Company',
                                        title=f'{product} - Projected Market Share',
                                        color_discrete_sequence=colors,
                                        hole=0.3
                                    )
                                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                                    fig_pie.update_layout(height=400, showlegend=True)
                                    st.plotly_chart(fig_pie, use_container_width=True)
                                
                                with col2:
                                    st.markdown("**📈 Company Performance Summary**")
                                    display_df = market_df.copy()
                                    display_df['Market Share (%)'] = display_df['Market Share (%)'].round(1)
                                    display_df['Growth Rate (%)'] = display_df['Growth Rate (%)'].round(1)
                                    display_df['Total Demand'] = display_df['Total Demand'].astype(int)
                                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                                    
                                    # Key insights
                                    leader = market_df.iloc[0]
                                    fastest_growth = market_df.loc[market_df['Growth Rate (%)'].idxmax()]
                                    
                                    st.markdown("**🔍 Key Insights:**")
                                    st.write(f"🏆 Market Leader: **{leader['Company']}** ({leader['Market Share (%)']:.1f}%)")
                                    st.write(f"📈 Fastest Growing: **{fastest_growth['Company']}** ({fastest_growth['Growth Rate (%)']:.1f}%)")
                                
                                st.markdown("---")
                            
                            elif len(company_forecasts) == 1:
                                st.info(f"ℹ️ Only one company has sufficient data for {product} comparison")
                            else:
                                st.warning(f"⚠️ Insufficient data for company comparison of {product}")
            else:
                # Show individual forecasts without tabs when no company comparison available
                st.markdown("### 📈 Product Forecasts")
                for product in selected_products:
                    if product in forecasts:
                        st.markdown(f"#### 🥛 {product}")
                        
                        forecast = forecasts[product]
                        
                        # Split historical and future data
                        if include_history:
                            # Find the split point (last actual data point)
                            today = datetime.now().date()
                            split_idx = len(forecast) - forecast_horizon
                            historical = forecast.iloc[:split_idx]
                            future = forecast.iloc[split_idx:]
                        else:
                            historical = pd.DataFrame()
                            future = forecast
                        
                        # Create forecast chart
                        fig = go.Figure()
                        
                        # Add historical data
                        if not historical.empty:
                            fig.add_trace(go.Scatter(
                                x=historical['ds'],
                                y=historical['yhat'],
                                mode='lines',
                                name='Historical',
                                line=dict(color='blue')
                            ))
                        
                        # Add forecast
                        fig.add_trace(go.Scatter(
                            x=future['ds'],
                            y=future['yhat'],
                            mode='lines',
                            name='Forecast',
                            line=dict(color='red', dash='dash')
                        ))
                        
                        # Add confidence interval
                        fig.add_trace(go.Scatter(
                            x=future['ds'].tolist() + future['ds'].tolist()[::-1],
                            y=future['yhat_upper'].tolist() + future['yhat_lower'].tolist()[::-1],
                            fill='toself',
                            fillcolor='rgba(255,0,0,0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='Confidence Interval'
                        ))
                        
                        fig.update_layout(
                            title=f'Demand Forecast - {product}',
                            xaxis_title='Date',
                            yaxis_title='Quantity',
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Forecast summary table
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**📊 Forecast Summary**")
                            future_summary = {
                                'Total Forecasted Demand': f"{future['yhat'].sum():.0f}",
                                'Average Daily Demand': f"{future['yhat'].mean():.0f}",
                                'Peak Daily Demand': f"{future['yhat'].max():.0f}",
                                'Minimum Daily Demand': f"{future['yhat'].min():.0f}"
                            }
                            
                            for key, value in future_summary.items():
                                st.write(f"• {key}: {value}")
                        
                        with col2:
                            st.write("**🎯 Confidence Ranges**")
                            confidence_summary = {
                                'Lower Bound (Total)': f"{future['yhat_lower'].sum():.0f}",
                                'Upper Bound (Total)': f"{future['yhat_upper'].sum():.0f}",
                                'Avg Confidence Width': f"{(future['yhat_upper'] - future['yhat_lower']).mean():.0f}",
                                'Forecast Trend': 'Increasing' if future['yhat'].iloc[-1] > future['yhat'].iloc[0] else 'Decreasing'
                            }
                            
                            for key, value in confidence_summary.items():
                                st.write(f"• {key}: {value}")

                            
                            # Split historical and future data
                            if include_history:
                                # Find the split point (last actual data point)
                                today = datetime.now().date()
                                split_idx = len(forecast) - forecast_horizon
                                historical = forecast.iloc[:split_idx]
                                future = forecast.iloc[split_idx:]
                            else:
                                historical = pd.DataFrame()
                                future = forecast
                            
                            # Create forecast chart
                            fig = go.Figure()
                            
                            # Add historical data
                            if not historical.empty:
                                fig.add_trace(go.Scatter(
                                    x=historical['ds'],
                                    y=historical['yhat'],
                                    mode='lines',
                                    name='Historical',
                                    line=dict(color='blue')
                                ))
                            
                            # Add forecast
                            fig.add_trace(go.Scatter(
                                x=future['ds'],
                                y=future['yhat'],
                                mode='lines',
                                name='Forecast',
                                line=dict(color='red', dash='dash')
                            ))
                            
                            # Add confidence interval
                            fig.add_trace(go.Scatter(
                                x=future['ds'].tolist() + future['ds'].tolist()[::-1],
                                y=future['yhat_upper'].tolist() + future['yhat_lower'].tolist()[::-1],
                                fill='toself',
                                fillcolor='rgba(255,0,0,0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                name='Confidence Interval'
                            ))
                            
                            fig.update_layout(
                                title=f'Demand Forecast - {product}',
                                xaxis_title='Date',
                                yaxis_title='Quantity',
                                hovermode='x unified',
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Forecast summary table
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**📊 Forecast Summary**")
                                future_summary = {
                                    'Total Forecasted Demand': f"{future['yhat'].sum():.0f}",
                                    'Average Daily Demand': f"{future['yhat'].mean():.0f}",
                                    'Peak Daily Demand': f"{future['yhat'].max():.0f}",
                                    'Minimum Daily Demand': f"{future['yhat'].min():.0f}"
                                }
                                
                                for key, value in future_summary.items():
                                    st.write(f"• {key}: {value}")
                            
                            with col2:
                                st.write("**🎯 Confidence Ranges**")
                                confidence_summary = {
                                    'Lower Bound (Total)': f"{future['yhat_lower'].sum():.0f}",
                                    'Upper Bound (Total)': f"{future['yhat_upper'].sum():.0f}",
                                    'Avg Confidence Width': f"{(future['yhat_upper'] - future['yhat_lower']).mean():.0f}",
                                    'Forecast Trend': 'Increasing' if future['yhat'].iloc[-1] > future['yhat'].iloc[0] else 'Decreasing'
                                }
                                
                                for key, value in confidence_summary.items():
                                    st.write(f"• {key}: {value}")
        
        # Production optimization section
        st.markdown("---")
        st.subheader("🏭 Production Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Safety stock configuration
            safety_stock = st.slider(
                            "Safety Stock (%)",
                            min_value=0,
                            max_value=50,
                            value=10,
                            help="Additional production buffer to handle demand uncertainty"
            )
            
            # Custom capacity settings
            st.write("**Production Capacities (units/day)**")
            custom_capacities = {}
            for product in selected_products:
                            if product in st.session_state.forecasts:
                                default_cap = optimizer.default_capacities.get(product, 1000)
                                custom_capacities[product] = st.number_input(
                                    f"{product}",
                                    min_value=100,
                                    max_value=10000,
                                    value=default_cap,
                                    step=50,
                                    key=f"capacity_{product}"
                                )
        
        with col2:
            if st.button("⚙️ Optimize Production", type="secondary"):
                            st.write("**🎯 Production Recommendations**")
                            
                            # Prepare forecast data for optimization
                            all_forecasts = []
                            for product in selected_products:
                                if product in st.session_state.forecasts:
                                    forecast_data = st.session_state.forecasts[product].tail(forecast_horizon).copy()
                                    forecast_data['product'] = product
                                    forecast_data = forecast_data.rename(columns={
                                        'ds': 'date',
                                        'yhat': 'predicted_demand'
                                    })
                                    all_forecasts.append(forecast_data[['date', 'product', 'predicted_demand']])
                            
                            if all_forecasts:
                                combined_forecasts = pd.concat(all_forecasts, ignore_index=True)
                                
                                # Generate optimization for each product
                                optimization_results = {}
                                for product in selected_products:
                                    if product in st.session_state.forecasts:
                                        production_plan = optimizer.calculate_optimal_production(
                                            combined_forecasts,
                                            product,
                                            safety_stock=safety_stock/100,
                                            custom_capacity=custom_capacities.get(product)
                                        )
                                        optimization_results[product] = production_plan
                                
                                # Display optimization results
                                for product, plan in optimization_results.items():
                                    if plan is not None:
                                        st.write(f"**{product}:**")
                                        avg_utilization = plan['capacity_utilization'].mean()
                                        total_production = plan['optimal_production'].sum()
                                        total_cost = plan['production_cost'].sum()
                                        
                                        col_a, col_b, col_c = st.columns(3)
                                        with col_a:
                                            st.metric("Avg Utilization", f"{avg_utilization:.1f}%")
                                        with col_b:
                                            st.metric("Total Production", f"{total_production:.0f}")
                                        with col_c:
                                            st.metric("Total Cost", f"₹{total_cost:,.0f}")
        
        # Detailed forecast table
        st.markdown("---")
        st.subheader("📋 Detailed Forecast Table")
        
        # Combine all forecasts into a single table
        detailed_forecasts = []
        for product in selected_products:
            if product in st.session_state.forecasts:
                            forecast_data = st.session_state.forecasts[product].tail(forecast_horizon).copy()
                            forecast_data['Product'] = product
                            forecast_data['Date'] = forecast_data['ds'].dt.strftime('%Y-%m-%d')
                            forecast_data['Predicted_Demand'] = forecast_data['yhat'].round(0)
                            forecast_data['Lower_Bound'] = forecast_data['yhat_lower'].round(0)
                            forecast_data['Upper_Bound'] = forecast_data['yhat_upper'].round(0)
                            
                            detailed_forecasts.append(forecast_data[['Date', 'Product', 'Predicted_Demand', 'Lower_Bound', 'Upper_Bound']])
        
        if detailed_forecasts:
            combined_table = pd.concat(detailed_forecasts, ignore_index=True)
            combined_table = combined_table.sort_values(['Date', 'Product'])
            
            st.dataframe(combined_table, use_container_width=True)
            
            # Export options
            st.markdown("---")
            st.subheader("📁 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                            # CSV export
                            csv_data = combined_table.to_csv(index=False)
                            st.download_button(
                    "📊 Download CSV",
                    csv_data,
                    file_name=f"demand_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel export option (placeholder)
                if st.button("📈 Generate Excel Report", use_container_width=True):
                    st.info("Excel report generation feature coming soon!")
            
            with col3:
                # PDF export option (placeholder)
                if st.button("📄 Generate PDF Report", use_container_width=True):
                    st.info("PDF report generation feature coming soon!")
    
    # Quick forecast summaries
    elif st.session_state.get('forecasts'):
        st.subheader("📊 Available Forecasts")
        
        forecast_summaries = []
        for product, forecast in st.session_state.forecasts.items():
            if len(forecast) > 0:
                last_30_days = forecast.tail(30)
                forecast_summaries.append({
                    'Product': product,
                    'Last_Updated': 'Recent',
                    'Avg_Daily_Demand': f"{last_30_days['yhat'].mean():.0f}",
                    'Total_30_Day_Demand': f"{last_30_days['yhat'].sum():.0f}",
                    'Trend': 'Increasing' if last_30_days['yhat'].iloc[-1] > last_30_days['yhat'].iloc[0] else 'Decreasing'
                })
        
        if forecast_summaries:
            summary_df = pd.DataFrame(forecast_summaries)
            st.dataframe(summary_df, use_container_width=True)
        
        if st.button("🔄 Generate New Forecasts"):
            st.rerun()
    
    else:
        st.info("👆 Configure your forecast parameters and click 'Generate Forecasts' to begin")
    
    # AI Analysis section
    if st.session_state.get('forecasts'):
        st.markdown("---")
        st.subheader("🤖 AI-Powered Analysis")
        
        # Initialize Gemini analyzer
        gemini_analyzer = GeminiAnalyzer()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Analyze Forecast Trends", type="secondary", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your forecast data..."):
                    insights = gemini_analyzer.analyze_forecast_data(st.session_state.forecasts)
                    
                    if insights:
                        st.markdown("#### 🎯 Key Business Insights")
                        
                        # Key trends
                        if insights.key_trends:
                            st.markdown("**📈 Identified Trends:**")
                            for trend in insights.key_trends:
                                st.write(f"• {trend}")
                        
                        # Business recommendations
                        if insights.business_recommendations:
                            st.markdown("**💡 Recommended Actions:**")
                            for rec in insights.business_recommendations:
                                st.write(f"• {rec}")
                        
                        # Risk factors
                        if insights.risk_factors:
                            st.markdown("**⚠️ Risk Factors:**")
                            for risk in insights.risk_factors:
                                st.warning(f"• {risk}")
                        
                        # Opportunities
                        if insights.opportunities:
                            st.markdown("**🚀 Growth Opportunities:**")
                            for opp in insights.opportunities:
                                st.success(f"• {opp}")
                        
                        # Confidence score
                        st.markdown(f"**🎯 AI Confidence Score: {insights.confidence_score:.1%}**")
                    
                    else:
                        st.error("Unable to generate AI analysis. Please check your API key configuration.")
        
        with col2:
            if st.button("🏆 Generate Competitive Analysis", type="secondary", use_container_width=True):
                if len(st.session_state.df['Company'].unique()) > 1:
                    with st.spinner("🤖 AI is analyzing competitive landscape..."):
                        # Prepare company comparison data
                        company_metrics = {}
                        for company in st.session_state.df['Company'].unique():
                            company_data = st.session_state.df[st.session_state.df['Company'] == company]
                            company_metrics[company] = {
                                'total_revenue': company_data['Revenue'].sum(),
                                'avg_price': company_data['Unit_Price'].mean(),
                                'total_volume': company_data['Quantity_Sold'].sum(),
                                'product_count': company_data['Product'].nunique(),
                                'market_presence': len(company_data)
                            }
                        
                        competitive_insights = gemini_analyzer.generate_competitive_analysis(company_metrics)
                        
                        if competitive_insights:
                            st.markdown("#### 🏆 Competitive Intelligence")
                            
                            # Market leader
                            st.markdown(f"**🥇 Market Leader:** {competitive_insights.market_leader}")
                            
                            # Growth opportunities
                            if competitive_insights.growth_opportunities:
                                st.markdown("**📈 Growth Opportunities:**")
                                for opp in competitive_insights.growth_opportunities:
                                    st.write(f"• {opp}")
                            
                            # Pricing insights
                            if competitive_insights.pricing_insights:
                                st.markdown("**💰 Pricing Insights:**")
                                for insight in competitive_insights.pricing_insights:
                                    st.info(f"• {insight}")
                            
                            # Strategic recommendations
                            if competitive_insights.strategic_recommendations:
                                st.markdown("**🎯 Strategic Recommendations:**")
                                for rec in competitive_insights.strategic_recommendations:
                                    st.write(f"• {rec}")
                        
                        else:
                            st.error("Unable to generate competitive analysis.")
                else:
                    st.warning("Competitive analysis requires data from multiple companies.")
        
        # Seasonal analysis
        if st.button("📅 Analyze Seasonal Patterns", use_container_width=True):
            with st.spinner("🤖 AI is analyzing seasonal patterns..."):
                # Prepare seasonal data
                seasonal_summary = {}
                if 'Season' in st.session_state.df.columns:
                    seasonal_data = st.session_state.df.groupby('Season').agg({
                        'Quantity_Sold': 'sum',
                        'Revenue': 'sum',
                        'Unit_Price': 'mean'
                    }).to_dict()
                    seasonal_summary = seasonal_data
                
                seasonal_insights = gemini_analyzer.analyze_seasonal_patterns(seasonal_summary)
                
                if seasonal_insights:
                    st.markdown("#### 📅 Seasonal Analysis Results")
                    st.markdown(seasonal_insights)
                else:
                    st.error("Unable to generate seasonal analysis.")
    
    # Tips section
    with st.expander("💡 Forecasting Tips & Insights", expanded=False):
        st.markdown("""
        **🎯 Understanding Your Forecasts:**
        
        **Confidence Intervals**
        - Wider intervals = higher uncertainty
        - Consider external factors not in historical data
        
        **Production Planning**
        - Use forecasts with safety stock for production planning
        - Consider capacity constraints and lead times
        - Monitor forecast accuracy and adjust safety stock accordingly
        
        **Optimization Guidelines**
        - Higher safety stock = lower stockout risk but higher inventory costs
        - Optimal capacity utilization is typically 70-85%
        - Consider seasonal patterns for capacity planning
        
        **Model Performance**
        - Regularly retrain models with new data
        - Monitor forecast accuracy over time
        - Account for special events and holidays
        """)

if __name__ == "__main__":
    main()
