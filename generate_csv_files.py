import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_company_data(company_name, num_records=5000):
    """Generate comprehensive dairy company data with all relevant columns."""
    
    # Define products for each company
    products = {
        'Mother Dairy': ['Milk', 'Butter', 'Cheese', 'Yogurt', 'Ghee', 'Paneer', 'Ice Cream', 'Curd', 'Lassi'],
        'Amul': ['Milk', 'Butter', 'Cheese', 'Yogurt', 'Ghee', 'Paneer', 'Ice Cream', 'Curd', 'Lassi', 'Chocolate'],
        'Heritage Foods': ['Milk', 'Butter', 'Cheese', 'Yogurt', 'Ghee', 'Paneer', 'Ice Cream', 'Curd', 'Lassi']
    }
    
    # Product-specific base prices and characteristics
    product_info = {
        'Milk': {'base_price': 55, 'seasonal_factor': 1.1, 'waste_rate': 0.02},
        'Butter': {'base_price': 450, 'seasonal_factor': 1.15, 'waste_rate': 0.01},
        'Cheese': {'base_price': 380, 'seasonal_factor': 1.08, 'waste_rate': 0.03},
        'Yogurt': {'base_price': 65, 'seasonal_factor': 1.12, 'waste_rate': 0.04},
        'Ghee': {'base_price': 520, 'seasonal_factor': 1.2, 'waste_rate': 0.01},
        'Paneer': {'base_price': 320, 'seasonal_factor': 1.18, 'waste_rate': 0.05},
        'Ice Cream': {'base_price': 180, 'seasonal_factor': 1.4, 'waste_rate': 0.08},
        'Curd': {'base_price': 45, 'seasonal_factor': 1.1, 'waste_rate': 0.06},
        'Lassi': {'base_price': 35, 'seasonal_factor': 1.25, 'waste_rate': 0.05},
        'Chocolate': {'base_price': 250, 'seasonal_factor': 1.3, 'waste_rate': 0.02}
    }
    
    # Company-specific factors
    company_factors = {
        'Mother Dairy': {'price_factor': 1.0, 'quality_factor': 0.95, 'efficiency': 0.92},
        'Amul': {'price_factor': 0.95, 'quality_factor': 1.0, 'efficiency': 0.95},
        'Heritage Foods': {'price_factor': 1.05, 'quality_factor': 0.9, 'efficiency': 0.88}
    }
    
    # Generate date range (3 years of data)
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    company_prods = products[company_name]
    factor = company_factors[company_name]
    
    for i in range(num_records):
        # Random date
        date = random.choice(date_range)
        year = date.year
        month = date.month
        day_of_year = date.timetuple().tm_yday
        
        # Random product
        product = random.choice(company_prods)
        prod_info = product_info[product]
        
        # Calculate seasonal effects
        seasonal_multiplier = 1 + 0.3 * np.sin(2 * np.pi * day_of_year / 365)
        if product == 'Ice Cream':
            # Higher demand in summer
            seasonal_multiplier = 1 + 0.6 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        elif product in ['Milk', 'Curd']:
            # More stable throughout year
            seasonal_multiplier = 1 + 0.1 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Price calculation with inflation and seasonal effects
        inflation_factor = 1 + (year - 2021) * 0.06  # 6% annual inflation
        base_price = prod_info['base_price'] * factor['price_factor']
        unit_price = base_price * inflation_factor * seasonal_multiplier * random.uniform(0.9, 1.1)
        
        # Quantity sold (influenced by price, season, and random factors)
        base_quantity = random.randint(100, 1000)
        price_sensitivity = -0.5  # Higher price = lower quantity
        price_effect = (unit_price / (base_price * inflation_factor)) ** price_sensitivity
        seasonal_demand = seasonal_multiplier * prod_info['seasonal_factor']
        
        quantity_sold = max(1, int(base_quantity * price_effect * seasonal_demand * random.uniform(0.7, 1.3)))
        
        # Production and inventory calculations
        production_quantity = int(quantity_sold * random.uniform(1.1, 1.4))  # Produce more than sold
        inventory_start = random.randint(50, 500)
        inventory_end = max(0, inventory_start + production_quantity - quantity_sold - random.randint(0, 50))
        
        # Cost calculations
        raw_material_cost_per_unit = unit_price * random.uniform(0.4, 0.6)
        processing_cost_per_unit = unit_price * random.uniform(0.1, 0.2)
        packaging_cost_per_unit = unit_price * random.uniform(0.05, 0.1)
        transportation_cost_per_unit = unit_price * random.uniform(0.03, 0.08)
        
        total_cost_per_unit = (raw_material_cost_per_unit + processing_cost_per_unit + 
                              packaging_cost_per_unit + transportation_cost_per_unit)
        
        # Waste calculations
        waste_quantity = int(production_quantity * prod_info['waste_rate'] * random.uniform(0.5, 1.5))
        waste_cost = waste_quantity * raw_material_cost_per_unit
        
        # Revenue and profit
        revenue = quantity_sold * unit_price
        total_costs = production_quantity * total_cost_per_unit + waste_cost
        profit = revenue - total_costs
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        # Quality metrics
        quality_score = factor['quality_factor'] * random.uniform(85, 98)
        customer_rating = min(5.0, quality_score / 20)
        
        # Operational metrics
        production_efficiency = factor['efficiency'] * random.uniform(0.85, 0.98)
        capacity_utilization = random.uniform(0.6, 0.95)
        
        # Market metrics
        market_share = random.uniform(0.15, 0.35) if company_name == 'Amul' else random.uniform(0.1, 0.25)
        competitor_price = unit_price * random.uniform(0.9, 1.1)
        
        record = {
            'Date': date.strftime('%Y-%m-%d'),
            'Company': company_name,
            'Product': product,
            'Quantity_Sold': quantity_sold,
            'Unit_Price': round(unit_price, 2),
            'Revenue': round(revenue, 2),
            'Production_Quantity': production_quantity,
            'Inventory_Start': inventory_start,
            'Inventory_End': inventory_end,
            'Raw_Material_Cost_Per_Unit': round(raw_material_cost_per_unit, 2),
            'Processing_Cost_Per_Unit': round(processing_cost_per_unit, 2),
            'Packaging_Cost_Per_Unit': round(packaging_cost_per_unit, 2),
            'Transportation_Cost_Per_Unit': round(transportation_cost_per_unit, 2),
            'Total_Cost_Per_Unit': round(total_cost_per_unit, 2),
            'Total_Costs': round(total_costs, 2),
            'Waste_Quantity': waste_quantity,
            'Waste_Cost': round(waste_cost, 2),
            'Profit': round(profit, 2),
            'Profit_Margin_Percent': round(profit_margin, 2),
            'Quality_Score': round(quality_score, 1),
            'Customer_Rating': round(customer_rating, 1),
            'Production_Efficiency': round(production_efficiency, 3),
            'Capacity_Utilization': round(capacity_utilization, 3),
            'Market_Share_Percent': round(market_share * 100, 2),
            'Competitor_Average_Price': round(competitor_price, 2),
            'Season': 'Summer' if month in [4, 5, 6] else 'Monsoon' if month in [7, 8, 9] else 'Winter' if month in [10, 11, 12] else 'Spring',
            'Region': random.choice(['North', 'South', 'East', 'West', 'Central']),
            'Sales_Channel': random.choice(['Retail', 'Wholesale', 'Online', 'Direct']),
            'Batch_Number': f'B{year}{month:02d}{random.randint(1000, 9999)}',
            'Expiry_Days': random.randint(3, 30) if product in ['Milk', 'Curd', 'Yogurt'] else random.randint(30, 365)
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

# Generate CSV files for all three companies
companies = ['Mother Dairy', 'Amul', 'Heritage Foods']

for company in companies:
    print(f"Generating data for {company}...")
    df = generate_company_data(company, 5000)
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Date', 'Product']).reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    filename = f"{company.replace(' ', '_').lower()}_data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Generated {filename} with {len(df)} records")
    print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"   Products: {df['Product'].nunique()} ({', '.join(df['Product'].unique())})")
    print(f"   Total Revenue: ₹{df['Revenue'].sum()/1000000:.1f}M")
    print()

print("🎉 All CSV files generated successfully!")