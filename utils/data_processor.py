import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class DataProcessor:
    """Handles data processing and validation for dairy sales data."""
    
    REQUIRED_COLUMNS = ['Date', 'Product', 'Quantity_Sold', 'Unit_Price']
    SUPPORTED_PRODUCTS = ['Milk', 'Butter', 'Cheese', 'Yogurt', 'Ghee', 'Paneer', 'Ice_Cream', 'Curd', 'Lassi', 'Chocolate']
    
    @staticmethod
    def load_preloaded_data():
        """Load the three preloaded CSV files and combine them into a single dataset."""
        try:
            # Load the three CSV files
            mother_dairy = pd.read_csv('mother_dairy_data.csv')
            amul = pd.read_csv('amul_data.csv') 
            heritage_foods = pd.read_csv('heritage_foods_data.csv')
            
            # Combine all datasets
            combined_df = pd.concat([mother_dairy, amul, heritage_foods], ignore_index=True)
            
            # Process the combined data
            combined_df = DataProcessor.preprocess_data(combined_df)
            
            return combined_df, True, "Successfully loaded 15,000 records from 3 dairy companies"
            
        except FileNotFoundError as e:
            return None, False, f"CSV files not found: {str(e)}"
        except Exception as e:
            return None, False, f"Error loading data: {str(e)}"
    
    @staticmethod
    def validate_csv(df):
        """Validate uploaded CSV data."""
        errors = []
        warnings = []
        
        # Check required columns
        missing_columns = set(DataProcessor.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        if errors:
            return False, errors, warnings
            
        # Check data types and values
        try:
            # Convert Date column
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            errors.append("Date column contains invalid date formats. Please use YYYY-MM-DD format.")
            
        # Check numeric columns
        for col in ['Quantity_Sold', 'Unit_Price']:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except:
                        errors.append(f"{col} contains non-numeric values")
                
                # Check for negative values
                if (df[col] < 0).any():
                    warnings.append(f"{col} contains negative values")
        
        # Check products
        if 'Product' in df.columns:
            unknown_products = set(df['Product'].unique()) - set(DataProcessor.SUPPORTED_PRODUCTS)
            if unknown_products:
                warnings.append(f"Unknown products found: {', '.join(unknown_products)}. Supported products: {', '.join(DataProcessor.SUPPORTED_PRODUCTS)}")
        
        # Check date range
        if 'Date' in df.columns and df['Date'].dtype == 'datetime64[ns]':
            date_range = df['Date'].max() - df['Date'].min()
            if date_range.days < 30:
                warnings.append("Dataset covers less than 30 days. More data recommended for better forecasting.")
            elif date_range.days < 90:
                warnings.append("Dataset covers less than 90 days. Consider adding more historical data.")
        
        return len(errors) == 0, errors, warnings
    
    @staticmethod
    def preprocess_data(df):
        """Preprocess the validated data for modeling."""
        # Create a copy
        processed_df = df.copy()
        
        # Ensure Date is datetime
        processed_df['Date'] = pd.to_datetime(processed_df['Date'])
        
        # Sort by date and product (handle Company column if it exists)
        if 'Company' in processed_df.columns:
            processed_df = processed_df.sort_values(['Company', 'Product', 'Date'])
        else:
            processed_df = processed_df.sort_values(['Product', 'Date'])
        
        # Add derived features
        processed_df['Revenue'] = processed_df['Quantity_Sold'] * processed_df['Unit_Price']
        processed_df['Year'] = processed_df['Date'].dt.year
        processed_df['Month'] = processed_df['Date'].dt.month
        processed_df['Day_of_Week'] = processed_df['Date'].dt.dayofweek
        processed_df['Day_of_Year'] = processed_df['Date'].dt.dayofyear
        
        return processed_df
    
    @staticmethod
    def get_data_summary(df):
        """Generate summary statistics for the dataset."""
        summary = {
            'total_records': len(df),
            'date_range': {
                'start': df['Date'].min(),
                'end': df['Date'].max(),
                'days': (df['Date'].max() - df['Date'].min()).days
            },
            'products': df['Product'].unique().tolist(),
            'product_counts': df['Product'].value_counts().to_dict(),
            'total_quantity': df['Quantity_Sold'].sum(),
            'total_revenue': (df['Quantity_Sold'] * df['Unit_Price']).sum(),
            'avg_daily_quantity': df.groupby('Date')['Quantity_Sold'].sum().mean(),
            'avg_unit_price': df.groupby('Product')['Unit_Price'].mean().to_dict()
        }
        return summary
    
    @staticmethod
    def prepare_prophet_data(df, product, company=None):
        """Prepare data for Prophet modeling."""
        # Create a copy and ensure Date is datetime
        df_copy = df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Date'])
        
        # Filter for specific product and company if provided
        if company:
            product_data = df_copy[(df_copy['Product'] == product) & (df_copy['Company'] == company)].copy()
        else:
            product_data = df_copy[df_copy['Product'] == product].copy()
        
        # Aggregate by date (in case multiple entries per day)
        group_cols = ['Date']
        agg_dict = {
            'Quantity_Sold': 'sum',
            'Unit_Price': 'mean'
        }
        
        # Add Revenue if not already present
        if 'Revenue' not in product_data.columns:
            product_data['Revenue'] = product_data['Quantity_Sold'] * product_data['Unit_Price']
        agg_dict['Revenue'] = 'sum'
        
        daily_data = product_data.groupby(group_cols).agg(agg_dict).reset_index()
        
        # Prepare for Prophet (requires 'ds' and 'y' columns)
        prophet_data = daily_data.rename(columns={
            'Date': 'ds',
            'Quantity_Sold': 'y'
        })
        
        # Ensure no missing dates
        date_range = pd.date_range(start=prophet_data['ds'].min(), 
                                 end=prophet_data['ds'].max(), 
                                 freq='D')
        prophet_data = prophet_data.set_index('ds').reindex(date_range).reset_index()
        prophet_data.columns = ['ds', 'y', 'Unit_Price', 'Revenue']
        
        # Fill missing values
        prophet_data['y'] = prophet_data['y'].fillna(0)
        prophet_data['Unit_Price'] = prophet_data['Unit_Price'].fillna(method='ffill').fillna(method='bfill')
        prophet_data['Revenue'] = prophet_data['Revenue'].fillna(0)
        
        return prophet_data
    
    @staticmethod
    def generate_sample_data():
        """Generate sample dairy sales data for testing."""
        np.random.seed(42)
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        products = {
            'Milk': {'base_quantity': 1200, 'base_price': 25, 'seasonality': 0.1},
            'Butter': {'base_quantity': 200, 'base_price': 450, 'seasonality': 0.15},
            'Cheese': {'base_quantity': 150, 'base_price': 350, 'seasonality': 0.2},
            'Yogurt': {'base_quantity': 300, 'base_price': 80, 'seasonality': 0.12},
            'Ghee': {'base_quantity': 100, 'base_price': 600, 'seasonality': 0.18}
        }
        
        data = []
        
        for date in date_range:
            for product, params in products.items():
                # Add seasonality (higher in winter months for some products)
                seasonal_factor = 1 + params['seasonality'] * np.sin(2 * np.pi * date.dayofyear / 365.25)
                
                # Add weekly pattern (higher on weekends)
                weekly_factor = 1.1 if date.weekday() >= 5 else 1.0
                
                # Add random noise
                noise_factor = 1 + np.random.normal(0, 0.1)
                
                # Calculate quantity
                quantity = int(params['base_quantity'] * seasonal_factor * weekly_factor * noise_factor)
                quantity = max(0, quantity)  # Ensure non-negative
                
                # Add some price variation
                price_variation = 1 + np.random.normal(0, 0.05)
                unit_price = params['base_price'] * price_variation
                
                data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Product': product,
                    'Quantity_Sold': quantity,
                    'Unit_Price': round(unit_price, 2)
                })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_multi_company_data():
        """Generate comprehensive sample data for multiple dairy companies (5000+ records)."""
        np.random.seed(42)
        
        # Extended date range for more data
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2024, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Define three different companies with varying characteristics
        companies = {
            'AmulFresh_Dairy': {
                'products': {
                    'Milk': {'base_quantity': 1500, 'base_price': 28, 'seasonality': 0.12, 'growth_rate': 0.05},
                    'Butter': {'base_quantity': 250, 'base_price': 480, 'seasonality': 0.18, 'growth_rate': 0.03},
                    'Cheese': {'base_quantity': 180, 'base_price': 380, 'seasonality': 0.22, 'growth_rate': 0.08},
                    'Yogurt': {'base_quantity': 400, 'base_price': 85, 'seasonality': 0.15, 'growth_rate': 0.06},
                    'Ghee': {'base_quantity': 120, 'base_price': 650, 'seasonality': 0.20, 'growth_rate': 0.04},
                    'Paneer': {'base_quantity': 90, 'base_price': 320, 'seasonality': 0.14, 'growth_rate': 0.07},
                    'Ice_Cream': {'base_quantity': 200, 'base_price': 150, 'seasonality': 0.35, 'growth_rate': 0.12}
                },
                'market_factor': 1.2,  # Premium brand
                'volatility': 0.08
            },
            'Heritage_Foods': {
                'products': {
                    'Milk': {'base_quantity': 1200, 'base_price': 25, 'seasonality': 0.10, 'growth_rate': 0.04},
                    'Butter': {'base_quantity': 200, 'base_price': 450, 'seasonality': 0.16, 'growth_rate': 0.02},
                    'Cheese': {'base_quantity': 150, 'base_price': 350, 'seasonality': 0.20, 'growth_rate': 0.06},
                    'Yogurt': {'base_quantity': 300, 'base_price': 80, 'seasonality': 0.12, 'growth_rate': 0.05},
                    'Ghee': {'base_quantity': 100, 'base_price': 600, 'seasonality': 0.18, 'growth_rate': 0.03},
                    'Paneer': {'base_quantity': 75, 'base_price': 300, 'seasonality': 0.13, 'growth_rate': 0.05},
                    'Curd': {'base_quantity': 180, 'base_price': 60, 'seasonality': 0.08, 'growth_rate': 0.04}
                },
                'market_factor': 1.0,  # Standard market
                'volatility': 0.10
            },
            'Mother_Dairy': {
                'products': {
                    'Milk': {'base_quantity': 1800, 'base_price': 26, 'seasonality': 0.09, 'growth_rate': 0.06},
                    'Butter': {'base_quantity': 280, 'base_price': 460, 'seasonality': 0.14, 'growth_rate': 0.04},
                    'Cheese': {'base_quantity': 200, 'base_price': 360, 'seasonality': 0.19, 'growth_rate': 0.07},
                    'Yogurt': {'base_quantity': 350, 'base_price': 82, 'seasonality': 0.11, 'growth_rate': 0.05},
                    'Ghee': {'base_quantity': 140, 'base_price': 620, 'seasonality': 0.17, 'growth_rate': 0.03},
                    'Ice_Cream': {'base_quantity': 150, 'base_price': 140, 'seasonality': 0.32, 'growth_rate': 0.10},
                    'Lassi': {'base_quantity': 120, 'base_price': 45, 'seasonality': 0.25, 'growth_rate': 0.08}
                },
                'market_factor': 1.1,  # Large scale operations
                'volatility': 0.06
            }
        }
        
        all_data = []
        
        for company_name, company_data in companies.items():
            products = company_data['products']
            market_factor = company_data['market_factor']
            volatility = company_data['volatility']
            
            for date in date_range:
                # Calculate days since start for growth trends
                days_elapsed = (date - start_date).days
                years_elapsed = days_elapsed / 365.25
                
                for product, params in products.items():
                    # Base parameters
                    base_quantity = params['base_quantity']
                    base_price = params['base_price']
                    seasonality = params['seasonality']
                    growth_rate = params['growth_rate']
                    
                    # Apply company-wide market factor
                    adjusted_quantity = base_quantity * market_factor
                    adjusted_price = base_price * market_factor
                    
                    # Add growth trend over time
                    growth_factor = (1 + growth_rate) ** years_elapsed
                    
                    # Seasonal patterns (different for each product)
                    seasonal_factor = 1 + seasonality * np.sin(2 * np.pi * date.dayofyear / 365.25)
                    
                    # Special seasonal boosts for certain products
                    if product == 'Ice_Cream' and date.month in [4, 5, 6, 7, 8]:  # Summer boost
                        seasonal_factor *= 1.5
                    elif product == 'Ghee' and date.month in [10, 11, 12, 1]:  # Festival season
                        seasonal_factor *= 1.3
                    elif product == 'Lassi' and date.month in [3, 4, 5, 6]:  # Hot weather
                        seasonal_factor *= 1.4
                    
                    # Weekly patterns
                    if date.weekday() >= 5:  # Weekend boost
                        weekly_factor = 1.15
                    elif date.weekday() == 0:  # Monday dip
                        weekly_factor = 0.9
                    else:
                        weekly_factor = 1.0
                    
                    # Monthly promotions (random)
                    if np.random.random() < 0.1:  # 10% chance of promotion
                        promotion_factor = 1.25
                    else:
                        promotion_factor = 1.0
                    
                    # Market volatility and random noise
                    market_noise = 1 + np.random.normal(0, volatility)
                    random_factor = 1 + np.random.normal(0, 0.05)
                    
                    # Calculate final quantity and price
                    final_quantity = int(adjusted_quantity * growth_factor * seasonal_factor * 
                                       weekly_factor * promotion_factor * market_noise * random_factor)
                    final_quantity = max(0, final_quantity)
                    
                    # Price variations
                    price_trend = 1 + (years_elapsed * 0.02)  # 2% annual inflation
                    price_volatility = 1 + np.random.normal(0, 0.03)
                    final_price = adjusted_price * price_trend * price_volatility
                    
                    # Add external factors (festivals, holidays)
                    if date.month == 11 and date.day in range(1, 15):  # Diwali season
                        final_quantity = int(final_quantity * 1.2)
                        final_price *= 1.05
                    elif date.month == 3 and date.day in range(8, 20):  # Holi season
                        if product in ['Milk', 'Paneer', 'Curd']:
                            final_quantity = int(final_quantity * 1.3)
                    
                    all_data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'Company': company_name,
                        'Product': product,
                        'Quantity_Sold': final_quantity,
                        'Unit_Price': round(final_price, 2),
                        'Region': np.random.choice(['North', 'South', 'East', 'West'], p=[0.3, 0.25, 0.25, 0.2]),
                        'Channel': np.random.choice(['Retail', 'Wholesale', 'Online'], p=[0.6, 0.3, 0.1])
                    })
        
        df = pd.DataFrame(all_data)
        
        # Add some missing data to make it realistic (2% missing values)
        missing_indices = np.random.choice(df.index, size=int(0.02 * len(df)), replace=False)
        for idx in missing_indices:
            if np.random.random() < 0.5:
                df.loc[idx, 'Quantity_Sold'] = 0  # Stockout days
            else:
                df.loc[idx, 'Unit_Price'] = df.loc[idx, 'Unit_Price'] * 0.9  # Discount days
        
        return df
