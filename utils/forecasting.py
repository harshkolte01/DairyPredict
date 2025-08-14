import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import streamlit as st
import warnings
import pickle
import os
from datetime import datetime
warnings.filterwarnings('ignore')

class DairyForecaster:
    """Handles time series forecasting for dairy products using Prophet."""
    
    def __init__(self):
        self.models = {}
        self.model_performance = {}
        self.models_dir = "models"
        self.metadata = {}
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
        
        # Load existing models on initialization
        self.load_all_models()
        
    def train_model(self, data, product, seasonality_mode='multiplicative'):
        """Train a Prophet model for a specific product."""
        try:
            # Initialize Prophet model with dairy-specific parameters
            model = Prophet(
                seasonality_mode=seasonality_mode,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                interval_width=0.95
            )
            
            # Add custom seasonalities for dairy products
            model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            
            # Fit the model
            with st.spinner(f'Training model for {product}...'):
                model.fit(data)
            
            # Store the model
            self.models[product] = model
            
            # Evaluate model performance
            self._evaluate_model(model, data, product)
            
            # Save the model to disk
            self.save_model(product, model, data)
            
            return True, f"Model trained successfully for {product}"
            
        except Exception as e:
            return False, f"Error training model for {product}: {str(e)}"
    
    def _evaluate_model(self, model, data, product):
        """Evaluate model performance using cross-validation metrics."""
        try:
            # Split data for validation (last 30 days)
            train_size = len(data) - 30
            if train_size < 60:  # Need minimum data for validation
                self.model_performance[product] = {
                    'mae': None,
                    'rmse': None,
                    'mape': None,
                    'note': 'Insufficient data for validation'
                }
                return
            
            train_data = data[:train_size]
            test_data = data[train_size:]
            
            # Train on subset
            temp_model = Prophet(
                seasonality_mode=model.seasonality_mode,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            temp_model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
            temp_model.fit(train_data)
            
            # Make predictions
            future = temp_model.make_future_dataframe(periods=len(test_data))
            forecast = temp_model.predict(future)
            
            # Calculate metrics
            y_true = test_data['y'].values
            y_pred = forecast.tail(len(test_data))['yhat'].values
            
            # Ensure no negative predictions for MAPE calculation
            y_pred = np.maximum(y_pred, 0.1)
            y_true = np.maximum(y_true, 0.1)
            
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mape = mean_absolute_percentage_error(y_true, y_pred) * 100
            
            self.model_performance[product] = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'note': 'Validation on last 30 days'
            }
            
        except Exception as e:
            self.model_performance[product] = {
                'mae': None,
                'rmse': None,
                'mape': None,
                'note': f'Error in validation: {str(e)}'
            }
    
    def generate_forecast(self, product, periods, include_history=True):
        """Generate forecast for a specific product."""
        if product not in self.models:
            return None, f"No trained model found for {product}"
        
        try:
            model = self.models[product]
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=periods, include_history=include_history)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Ensure non-negative predictions
            forecast['yhat'] = np.maximum(forecast['yhat'], 0)
            forecast['yhat_lower'] = np.maximum(forecast['yhat_lower'], 0)
            forecast['yhat_upper'] = np.maximum(forecast['yhat_upper'], 0)
            
            return forecast, "Forecast generated successfully"
            
        except Exception as e:
            return None, f"Error generating forecast for {product}: {str(e)}"
    
    def get_forecast_summary(self, product, periods_list=[7, 14, 30]):
        """Get forecast summary for multiple periods."""
        if product not in self.models:
            return None
        
        summaries = {}
        
        for periods in periods_list:
            forecast, _ = self.generate_forecast(product, periods, include_history=False)
            if forecast is not None:
                # Get future predictions only
                future_forecast = forecast.tail(periods)
                
                summaries[f'{periods}_days'] = {
                    'total_demand': future_forecast['yhat'].sum(),
                    'avg_daily_demand': future_forecast['yhat'].mean(),
                    'max_daily_demand': future_forecast['yhat'].max(),
                    'min_daily_demand': future_forecast['yhat'].min(),
                    'trend': 'increasing' if future_forecast['yhat'].iloc[-1] > future_forecast['yhat'].iloc[0] else 'decreasing',
                    'confidence_range': {
                        'lower': future_forecast['yhat_lower'].sum(),
                        'upper': future_forecast['yhat_upper'].sum()
                    }
                }
        
        return summaries
    
    def get_model_components(self, product):
        """Get model components (trend, seasonality) for analysis."""
        if product not in self.models:
            return None
        
        try:
            model = self.models[product]
            
            # Generate forecast for components
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
            # Get components
            components = {}
            
            if 'trend' in forecast.columns:
                components['trend'] = forecast[['ds', 'trend']].tail(90)
            
            if 'weekly' in forecast.columns:
                components['weekly'] = forecast[['ds', 'weekly']].tail(90)
                
            if 'yearly' in forecast.columns:
                components['yearly'] = forecast[['ds', 'yearly']].tail(90)
                
            if 'monthly' in forecast.columns:
                components['monthly'] = forecast[['ds', 'monthly']].tail(90)
            
            return components
            
        except Exception as e:
            return None
    
    def export_forecasts(self, products, periods=30):
        """Export forecasts for multiple products to a DataFrame."""
        all_forecasts = []
        
        for product in products:
            if product in self.models:
                forecast, _ = self.generate_forecast(product, periods, include_history=False)
                if forecast is not None:
                    forecast_subset = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                    forecast_subset['product'] = product
                    forecast_subset = forecast_subset.rename(columns={
                        'ds': 'date',
                        'yhat': 'predicted_demand',
                        'yhat_lower': 'lower_bound',
                        'yhat_upper': 'upper_bound'
                    })
                    all_forecasts.append(forecast_subset)
        
        if all_forecasts:
            return pd.concat(all_forecasts, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_training_status(self):
        """Get status of all trained models."""
        status = {}
        for product, model in self.models.items():
            metadata = self.metadata.get(product, {})
            status[product] = {
                'trained': True,
                'performance': self.model_performance.get(product, {}),
                'last_training': metadata.get('trained_date', 'Recently'),
                'data_points': metadata.get('data_points', 'Unknown')
            }
        return status
    
    def save_model(self, product, model, training_data):
        """Save trained model to disk with metadata."""
        try:
            model_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_model.pkl")
            performance_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_performance.pkl")
            metadata_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_metadata.pkl")
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Save performance metrics
            performance = self.model_performance.get(product, {})
            with open(performance_path, 'wb') as f:
                pickle.dump(performance, f)
            
            # Save metadata
            metadata = {
                'product': product,
                'trained_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_points': len(training_data),
                'date_range': {
                    'start': training_data['ds'].min().strftime('%Y-%m-%d'),
                    'end': training_data['ds'].max().strftime('%Y-%m-%d')
                }
            }
            
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            # Store metadata in memory
            self.metadata[product] = metadata
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save model for {product}: {str(e)}")
            return False
    
    def load_model(self, product):
        """Load a saved model from disk."""
        try:
            model_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_model.pkl")
            performance_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_performance.pkl")
            metadata_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_metadata.pkl")
            
            # Check if all files exist
            if not all(os.path.exists(path) for path in [model_path, performance_path, metadata_path]):
                return False
            
            # Load model
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Load performance
            with open(performance_path, 'rb') as f:
                performance = pickle.load(f)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Store in memory
            self.models[product] = model
            self.model_performance[product] = performance
            self.metadata[product] = metadata
            
            return True
            
        except Exception as e:
            return False
    
    def load_all_models(self):
        """Load all available saved models."""
        if not os.path.exists(self.models_dir):
            return
        
        # Find all model files
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('_model.pkl')]
        
        loaded_count = 0
        for model_file in model_files:
            # Extract product name from filename
            product = model_file.replace('_model.pkl', '').replace('_', ' ')
            
            if self.load_model(product):
                loaded_count += 1
        
        if loaded_count > 0:
            print(f"Loaded {loaded_count} pre-trained models")
    
    def delete_model(self, product):
        """Delete a saved model from disk and memory."""
        try:
            model_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_model.pkl")
            performance_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_performance.pkl")
            metadata_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_metadata.pkl")
            
            # Remove files if they exist
            for path in [model_path, performance_path, metadata_path]:
                if os.path.exists(path):
                    os.remove(path)
            
            # Remove from memory
            if product in self.models:
                del self.models[product]
            if product in self.model_performance:
                del self.model_performance[product]
            if product in self.metadata:
                del self.metadata[product]
            
            return True
            
        except Exception as e:
            return False
    
    def get_available_models(self):
        """Get list of available pre-trained models."""
        if not os.path.exists(self.models_dir):
            return []
        
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('_model.pkl')]
        products = [f.replace('_model.pkl', '').replace('_', ' ') for f in model_files]
        
        return products
    
    def model_exists(self, product):
        """Check if a pre-trained model exists for a product."""
        model_path = os.path.join(self.models_dir, f"{product.replace(' ', '_')}_model.pkl")
        return os.path.exists(model_path)
