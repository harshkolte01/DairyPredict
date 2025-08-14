import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ProductionOptimizer:
    """Handles production optimization and capacity planning for dairy plants."""
    
    def __init__(self):
        # Default capacity constraints (units per day)
        self.default_capacities = {
            'Milk': 2000,
            'Butter': 500,
            'Cheese': 400,
            'Yogurt': 800,
            'Ghee': 300
        }
        
        # Production costs (per unit)
        self.production_costs = {
            'Milk': 15,
            'Butter': 300,
            'Cheese': 250,
            'Yogurt': 50,
            'Ghee': 400
        }
        
        # Storage costs (per unit per day)
        self.storage_costs = {
            'Milk': 0.5,
            'Butter': 2.0,
            'Cheese': 3.0,
            'Yogurt': 1.0,
            'Ghee': 2.5
        }
        
        # Shelf life (days)
        self.shelf_life = {
            'Milk': 5,
            'Butter': 30,
            'Cheese': 45,
            'Yogurt': 10,
            'Ghee': 90
        }
    
    def calculate_optimal_production(self, forecasts, product, safety_stock=0.1, custom_capacity=None):
        """Calculate optimal production quantities based on forecasts."""
        if forecasts is None or len(forecasts) == 0:
            return None
        
        # Get capacity constraint
        capacity = custom_capacity or self.default_capacities.get(product, 1000)
        
        # Get forecasts for the product
        product_forecasts = forecasts[forecasts['product'] == product].copy() if 'product' in forecasts.columns else forecasts.copy()
        
        if len(product_forecasts) == 0:
            return None
        
        # Sort by date
        product_forecasts = product_forecasts.sort_values('date' if 'date' in product_forecasts.columns else 'ds')
        
        # Calculate optimal production
        optimal_production = []
        
        for _, row in product_forecasts.iterrows():
            forecast_demand = row['predicted_demand'] if 'predicted_demand' in row else row['yhat']
            
            # Add safety stock
            adjusted_demand = forecast_demand * (1 + safety_stock)
            
            # Apply capacity constraint
            production_qty = min(adjusted_demand, capacity)
            
            # Calculate utilization
            utilization = (production_qty / capacity) * 100
            
            # Calculate costs
            prod_cost = production_qty * self.production_costs.get(product, 0)
            
            # Calculate potential revenue (using average price)
            avg_price = self._estimate_price(product)
            potential_revenue = production_qty * avg_price
            
            optimal_production.append({
                'date': row['date'] if 'date' in row else row['ds'],
                'forecasted_demand': forecast_demand,
                'optimal_production': round(production_qty, 0),
                'capacity_utilization': round(utilization, 1),
                'production_cost': round(prod_cost, 2),
                'potential_revenue': round(potential_revenue, 2),
                'profit_margin': round(((potential_revenue - prod_cost) / potential_revenue) * 100, 1) if potential_revenue > 0 else 0
            })
        
        return pd.DataFrame(optimal_production)
    
    def _estimate_price(self, product):
        """Estimate average selling price for a product."""
        price_estimates = {
            'Milk': 25,
            'Butter': 450,
            'Cheese': 350,
            'Yogurt': 80,
            'Ghee': 600
        }
        return price_estimates.get(product, 100)
    
    def calculate_inventory_optimization(self, forecasts, product, current_inventory=0):
        """Calculate optimal inventory levels to minimize waste and stockouts."""
        if forecasts is None or len(forecasts) == 0:
            return None
        
        product_forecasts = forecasts[forecasts['product'] == product].copy() if 'product' in forecasts.columns else forecasts.copy()
        
        if len(product_forecasts) == 0:
            return None
        
        shelf_life_days = self.shelf_life.get(product, 30)
        storage_cost_per_day = self.storage_costs.get(product, 1.0)
        
        inventory_plan = []
        current_stock = current_inventory
        
        for i, row in product_forecasts.iterrows():
            date = row['date'] if 'date' in row else row['ds']
            demand = row['predicted_demand'] if 'predicted_demand' in row else row['yhat']
            
            # Calculate optimal stock level (considering shelf life)
            future_demand = self._calculate_future_demand(product_forecasts, i, shelf_life_days)
            optimal_stock = min(future_demand, demand * shelf_life_days)
            
            # Calculate reorder point
            reorder_point = demand * 2  # 2 days safety stock
            
            # Calculate recommended order quantity
            if current_stock < reorder_point:
                order_qty = optimal_stock - current_stock
            else:
                order_qty = 0
            
            # Update current stock
            current_stock = max(0, current_stock + order_qty - demand)
            
            # Calculate storage cost
            daily_storage_cost = current_stock * storage_cost_per_day
            
            inventory_plan.append({
                'date': date,
                'current_inventory': round(current_stock, 0),
                'forecasted_demand': round(demand, 0),
                'optimal_stock_level': round(optimal_stock, 0),
                'reorder_point': round(reorder_point, 0),
                'recommended_order': round(order_qty, 0),
                'daily_storage_cost': round(daily_storage_cost, 2),
                'stock_status': self._get_stock_status(current_stock, reorder_point, optimal_stock)
            })
        
        return pd.DataFrame(inventory_plan)
    
    def _calculate_future_demand(self, forecasts, current_index, days):
        """Calculate total demand for next N days."""
        end_index = min(current_index + days, len(forecasts))
        future_data = forecasts.iloc[current_index:end_index]
        
        demand_col = 'predicted_demand' if 'predicted_demand' in future_data.columns else 'yhat'
        return future_data[demand_col].sum()
    
    def _get_stock_status(self, current_stock, reorder_point, optimal_stock):
        """Determine stock status based on levels."""
        if current_stock < reorder_point:
            return "Reorder Required"
        elif current_stock > optimal_stock:
            return "Overstock"
        else:
            return "Optimal"
    
    def calculate_capacity_utilization(self, production_plan, custom_capacities=None):
        """Calculate overall capacity utilization across all products."""
        if production_plan is None or len(production_plan) == 0:
            return None
        
        capacities = custom_capacities or self.default_capacities
        
        utilization_data = []
        
        # Group by date
        if 'date' in production_plan.columns:
            daily_production = production_plan.groupby('date').agg({
                'optimal_production': 'sum',
                'capacity_utilization': 'mean'
            }).reset_index()
            
            for _, row in daily_production.iterrows():
                utilization_data.append({
                    'date': row['date'],
                    'total_production': row['optimal_production'],
                    'avg_utilization': round(row['capacity_utilization'], 1),
                    'utilization_status': self._get_utilization_status(row['capacity_utilization'])
                })
        
        return pd.DataFrame(utilization_data)
    
    def _get_utilization_status(self, utilization):
        """Determine utilization status."""
        if utilization < 60:
            return "Under-utilized"
        elif utilization > 90:
            return "Over-utilized"
        else:
            return "Optimal"
    
    def generate_optimization_summary(self, forecasts, products, time_horizon=30):
        """Generate comprehensive optimization summary."""
        summary = {
            'total_products': len(products),
            'time_horizon_days': time_horizon,
            'optimization_date': datetime.now().strftime('%Y-%m-%d'),
            'products_analysis': {}
        }
        
        total_production_cost = 0
        total_potential_revenue = 0
        
        for product in products:
            production_plan = self.calculate_optimal_production(forecasts, product)
            
            if production_plan is not None and len(production_plan) > 0:
                product_summary = {
                    'total_forecasted_demand': production_plan['forecasted_demand'].sum(),
                    'total_optimal_production': production_plan['optimal_production'].sum(),
                    'avg_capacity_utilization': production_plan['capacity_utilization'].mean(),
                    'total_production_cost': production_plan['production_cost'].sum(),
                    'total_potential_revenue': production_plan['potential_revenue'].sum(),
                    'avg_profit_margin': production_plan['profit_margin'].mean(),
                    'capacity_constraint': self.default_capacities.get(product, 'Unknown'),
                    'recommendations': self._generate_product_recommendations(production_plan)
                }
                
                summary['products_analysis'][product] = product_summary
                total_production_cost += product_summary['total_production_cost']
                total_potential_revenue += product_summary['total_potential_revenue']
        
        # Overall summary
        summary['overall_metrics'] = {
            'total_production_cost': round(total_production_cost, 2),
            'total_potential_revenue': round(total_potential_revenue, 2),
            'overall_profit_margin': round(((total_potential_revenue - total_production_cost) / total_potential_revenue) * 100, 1) if total_potential_revenue > 0 else 0
        }
        
        return summary
    
    def _generate_product_recommendations(self, production_plan):
        """Generate recommendations based on production plan analysis."""
        recommendations = []
        
        avg_utilization = production_plan['capacity_utilization'].mean()
        
        if avg_utilization < 60:
            recommendations.append("Consider increasing production capacity utilization or reducing fixed costs")
        elif avg_utilization > 90:
            recommendations.append("Consider expanding production capacity to meet demand")
        
        if production_plan['profit_margin'].mean() < 20:
            recommendations.append("Review pricing strategy or production costs to improve margins")
        
        # Check for demand variability
        demand_std = production_plan['forecasted_demand'].std()
        demand_mean = production_plan['forecasted_demand'].mean()
        
        if demand_mean > 0 and (demand_std / demand_mean) > 0.3:
            recommendations.append("High demand variability detected - consider flexible production scheduling")
        
        return recommendations
