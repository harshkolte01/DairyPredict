# Overview

This is a comprehensive Dairy Plant Demand Forecasting System built with Streamlit that enables dairy producers to analyze historical sales data, train AI forecasting models, and generate production recommendations. The application provides an end-to-end solution for demand prediction using Prophet time series analysis, production optimization, and detailed reporting capabilities for dairy products including milk, butter, cheese, yogurt, ghee, paneer, ice cream, curd, and lassi.

## Recent Updates (August 2025)
- Successfully migrated from Replit Agent to standard Replit environment
- Removed standalone Model Evaluation page and integrated evaluation functionality into Model Training page
- Enhanced Model Training page to show comprehensive evaluation metrics after training completion
- Updated navigation across all pages to reflect new simplified structure
- Fixed all UI components to use unified navigation without separate evaluation page
- Optimized application structure for better user workflow and reduced complexity
- **NEW: Model Persistence System** - Trained models are now automatically saved to disk and can be reused without retraining
- Added comprehensive company comparison functionality for competitive demand analysis across dairy companies
- Enhanced forecasting with market share visualization, growth rate analysis, and competitive rankings

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit with multi-page application structure
- **UI Pattern**: Dashboard-driven interface with sidebar navigation
- **State Management**: Session-based state management using `st.session_state` for data persistence across pages
- **Visualization**: Plotly for interactive charts and graphs (Express and Graph Objects)
- **Layout**: Wide layout configuration with responsive column-based design

## Backend Architecture
- **Core Processing**: Modular utility classes for data processing, forecasting, and optimization
- **Data Processing**: `DataProcessor` class handles CSV validation and data cleaning with predefined schemas
- **Forecasting Engine**: `DairyForecaster` class implements Prophet-based time series modeling with dairy-specific seasonality
- **Optimization Engine**: `ProductionOptimizer` class manages capacity planning and production recommendations
- **Model Persistence**: Automatic save/load functionality using pickle serialization with metadata tracking
- **Model Storage**: Models saved to `/models` directory with performance metrics and training metadata

## Data Architecture
- **Input Format**: CSV files with required columns (Date, Product, Quantity_Sold, Unit_Price)
- **Product Categories**: Predefined dairy products (Milk, Butter, Cheese, Yogurt, Ghee)
- **Time Series Structure**: Daily granularity with support for multiple seasonality patterns
- **Validation Layer**: Comprehensive data validation including type checking and business rule enforcement

## Application Flow
- **Page Structure**: Five main pages - Dashboard, Data Upload, Model Training, Forecasting, Reports
- **Workflow**: Sequential process from data upload → model training → forecasting → reporting
- **State Tracking**: Session state variables track data upload status, model training completion, forecast availability
- **Model Persistence**: Automatic model saving and loading eliminates need for retraining on app restart
- **Multi-Company Support**: Enhanced workflow supporting comparative analysis across multiple dairy companies
- **Company Comparison**: Dedicated forecasting features for competitive demand analysis with market share visualization

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework and UI components
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing operations
- **Prophet**: Facebook's time series forecasting library for demand prediction
- **Plotly**: Interactive visualization library (Express and Graph Objects)
- **Scikit-learn**: Machine learning metrics for model evaluation (MAE, MSE, MAPE)

## Python Standard Library
- **datetime**: Date and time manipulation for time series operations
- **time**: Progress tracking and timing operations
- **json**: Data serialization for reports
- **io**: File operations and data streaming
- **warnings**: Error handling and filtering

## Data Format Requirements
- **CSV Input**: Structured historical sales data
- **Date Format**: YYYY-MM-DD standardized format
- **Numeric Validation**: Quantity and price fields with non-negative constraints
- **Product Standardization**: Predefined product categories for consistency