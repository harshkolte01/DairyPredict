import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
from utils.forecasting import DairyForecaster
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

st.set_page_config(page_title="Model Training", page_icon="🤖", layout="wide")

def main():
    st.title("🤖 Model Training")
    st.markdown("Train AI models for demand forecasting using Prophet time series analysis")
    
    # Check if data is available
    if not st.session_state.get('data_uploaded', False) or st.session_state.df is None:
        st.warning("📁 No data available for training. Please upload data first.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 Upload Data"):
                st.switch_page("pages/2_📁_Data_Upload.py")
        with col2:
            if st.button("📊 View Dashboard"):
                st.switch_page("pages/1_📊_Dashboard.py")
        return
    
    df = st.session_state.df
    
    # Initialize forecaster
    if 'forecaster' not in st.session_state:
        st.session_state.forecaster = DairyForecaster()
    
    forecaster = st.session_state.forecaster
    
    # Show available pre-trained models
    if hasattr(forecaster, 'get_available_models'):
        available_models = forecaster.get_available_models()
        if available_models:
            st.success(f"📁 Found {len(available_models)} pre-trained models: {', '.join(available_models)}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Use Existing Models", type="secondary"):
                    st.session_state.models_trained = True
                    st.session_state.forecaster = forecaster
                    st.success("✅ Pre-trained models loaded successfully!")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear All Models", type="secondary"):
                    for model in available_models:
                        forecaster.delete_model(model)
                    st.success("🗑️ All saved models have been cleared")
                    st.rerun()
    
    # Training configuration
    st.subheader("⚙️ Training Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select products to train
        available_products = df['Product'].unique().tolist()
        selected_products = st.multiselect(
            "Select Products to Train",
            available_products,
            default=available_products,
            help="Choose which products to train models for"
        )
        
        # Seasonality mode
        seasonality_mode = st.selectbox(
            "Seasonality Mode",
            ['multiplicative', 'additive'],
            index=0,
            help="Multiplicative: seasonal effects scale with trend. Additive: constant seasonal effects"
        )
    
    with col2:
        # Data split information
        st.info("📊 **Data Overview**")
        st.write(f"• Total records: {len(df):,}")
        st.write(f"• Date range: {(df['Date'].max() - df['Date'].min()).days} days")
        st.write(f"• Products available: {len(available_products)}")
        
        # Training parameters info
        st.info("🔧 **Training Parameters**")
        st.write("• Algorithm: Facebook Prophet")
        st.write("• Validation: Last 30 days")
        st.write("• Changepoint detection: Automatic")
        st.write("• Confidence interval: 95%")
    
    # Data preparation preview
    if selected_products:
        st.subheader("📋 Data Preparation Preview")
        
        # Show sample prepared data for first product
        sample_product = selected_products[0]
        prophet_data = DataProcessor.prepare_prophet_data(df, sample_product)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Sample data for {sample_product}:**")
            st.dataframe(prophet_data.head(10), use_container_width=True)
        
        with col2:
            # Quick visualization
            fig = px.line(prophet_data.tail(90), x='ds', y='y',
                         title=f'Recent Demand - {sample_product}',
                         labels={'ds': 'Date', 'y': 'Quantity'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Training section
    st.markdown("---")
    st.subheader("🚀 Model Training")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🏋️ Train Models", type="primary", use_container_width=True, disabled=not selected_products):
            if not selected_products:
                st.error("❌ Please select at least one product to train")
                return
            
            # Training progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            training_results = []
            
            for i, product in enumerate(selected_products):
                status_text.text(f"Training model for {product}...")
                progress_bar.progress((i) / len(selected_products))
                
                # Prepare data for this product
                prophet_data = DataProcessor.prepare_prophet_data(df, product)
                
                # Train model
                success, message = forecaster.train_model(prophet_data, product, seasonality_mode)
                
                training_results.append({
                    'Product': product,
                    'Status': '✅ Success' if success else '❌ Failed',
                    'Message': message,
                    'Data Points': len(prophet_data)
                })
                
                progress_bar.progress((i + 1) / len(selected_products))
                time.sleep(0.5)  # Small delay for visual feedback
            
            progress_bar.progress(1.0)
            status_text.text("Training completed!")
            
            # Show training results
            st.subheader("📊 Training Results")
            
            results_df = pd.DataFrame(training_results)
            st.dataframe(results_df, use_container_width=True)
            
            # Update session state
            successful_trainings = sum(1 for result in training_results if 'Success' in result['Status'])
            if successful_trainings > 0:
                st.session_state.models_trained = True
                st.success(f"🎉 Successfully trained {successful_trainings} model(s)!")
                
                # Navigation buttons
                col_nav1, col_nav2 = st.columns(2)
                with col_nav1:
                    if st.button("📈 Generate Forecasts", help="Create demand forecasts"):
                        st.switch_page("pages/4_📈_Forecasting.py")
                with col_nav2:
                    if st.button("📊 View Dashboard", help="Return to main dashboard"):
                        st.switch_page("pages/1_📊_Dashboard.py")
            else:
                st.error("❌ No models were trained successfully")
    
    # Model performance section
    if forecaster.models:
        st.markdown("---")
        st.subheader("📈 Model Performance")
        
        performance_data = []
        for product, performance in forecaster.model_performance.items():
            if performance:
                performance_data.append({
                    'Product': product,
                    'MAE': f"{performance.get('mae', 0):.2f}" if performance.get('mae') is not None else 'N/A',
                    'RMSE': f"{performance.get('rmse', 0):.2f}" if performance.get('rmse') is not None else 'N/A',
                    'MAPE (%)': f"{performance.get('mape', 0):.2f}" if performance.get('mape') is not None else 'N/A',
                    'Note': performance.get('note', 'Validation completed')
                })
        
        if performance_data:
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, use_container_width=True)
            
            # Performance interpretation
            with st.expander("📚 How to Interpret Performance Metrics", expanded=False):
                st.markdown("""
                **MAE (Mean Absolute Error)**: Average difference between predicted and actual values
                - Lower is better
                - Same units as your data
                
                **RMSE (Root Mean Square Error)**: Square root of average squared differences
                - Lower is better
                - Penalizes larger errors more than MAE
                
                **MAPE (Mean Absolute Percentage Error)**: Average percentage error
                - Lower is better
                - < 10%: Excellent
                - 10-20%: Good
                - 20-50%: Reasonable
                - > 50%: Poor
                """)
        
        # Model components visualization
        st.subheader("🔍 Model Components Analysis")
        
        product_for_analysis = st.selectbox(
            "Select Product for Component Analysis",
            list(forecaster.models.keys()),
            help="View trend and seasonality components"
        )
        
        if product_for_analysis:
            components = forecaster.get_model_components(product_for_analysis)
            
            if components:
                # Create subplots for components
                fig = make_subplots(
                    rows=len(components), cols=1,
                    subplot_titles=list(components.keys()),
                    vertical_spacing=0.1
                )
                
                for i, (component_name, component_data) in enumerate(components.items()):
                    fig.add_trace(
                        go.Scatter(
                            x=component_data['ds'],
                            y=component_data.iloc[:, 1],
                            mode='lines',
                            name=component_name,
                            showlegend=False
                        ),
                        row=i+1, col=1
                    )
                
                fig.update_layout(height=200*len(components), title_text=f"Model Components - {product_for_analysis}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No component data available for analysis")
    
    # Enhanced training status with persistence info
    st.markdown("---")
    st.subheader("📋 Training Status & Model Management")
    
    if forecaster.models:
        status = forecaster.get_training_status()
        status_data = []
        
        for product, info in status.items():
            metadata = forecaster.metadata.get(product, {})
            status_data.append({
                'Product': product,
                'Status': '✅ Trained & Saved' if info['trained'] else '❌ Not Trained',
                'Last Training': info['last_training'],
                'Data Points': info.get('data_points', 'Unknown'),
                'Date Range': f"{metadata.get('date_range', {}).get('start', 'N/A')} to {metadata.get('date_range', {}).get('end', 'N/A')}",
                'Performance': 'Available' if info['performance'] else 'N/A'
            })
        
        status_df = pd.DataFrame(status_data)
        st.dataframe(status_df, use_container_width=True)
        
        # Model management options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Verify Saved Models"):
                saved_count = 0
                for product in forecaster.models.keys():
                    if forecaster.model_exists(product):
                        saved_count += 1
                st.success(f"✅ {saved_count}/{len(forecaster.models)} models are saved to disk")
        
        with col2:
            if st.button("🎯 Generate Forecasts"):
                st.switch_page("pages/4_📈_Forecasting.py")
        
        with col3:
            selected_product_to_delete = st.selectbox(
                "Delete Model",
                ['Select...'] + list(forecaster.models.keys()),
                key="delete_model_select"
            )
            if selected_product_to_delete != 'Select...' and st.button("🗑️ Delete", key="delete_button"):
                if forecaster.delete_model(selected_product_to_delete):
                    st.success(f"✅ Deleted {selected_product_to_delete}")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to delete {selected_product_to_delete}")
    else:
        st.info("👋 No models trained yet. Start by configuring and training your first model above.")
    
    # Tips and recommendations
    with st.expander("💡 Training Tips & Best Practices", expanded=False):
        st.markdown("""
        **For Better Model Performance:**
        
        🔸 **Data Quality**
        - Ensure consistent data collection
        - Include at least 3-6 months of historical data
        - Handle outliers and anomalies appropriately
        
        🔸 **Seasonality Mode Selection**
        - **Multiplicative**: Use when seasonal effects change proportionally with trend
        - **Additive**: Use when seasonal effects are constant over time
        
        🔸 **Model Validation**
        - MAPE < 20% is generally considered good for demand forecasting
        - Monitor model performance over time
        - Retrain models with new data periodically
        
        🔸 **Product-Specific Considerations**
        - Different products may have different seasonal patterns
        - Consider external factors (holidays, weather, etc.)
        - Account for product lifecycle stages
        """)

if __name__ == "__main__":
    main()
