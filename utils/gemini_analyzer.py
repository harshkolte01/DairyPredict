import json
import logging
import os
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel
import streamlit as st

class ForecastInsights(BaseModel):
    key_trends: list[str]
    business_recommendations: list[str]
    risk_factors: list[str]
    opportunities: list[str]
    confidence_score: float

class CompetitiveAnalysis(BaseModel):
    market_leader: str
    growth_opportunities: list[str]
    pricing_insights: list[str]
    strategic_recommendations: list[str]

class GeminiAnalyzer:
    """AI-powered analysis using Google Gemini for dairy forecasting insights."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with API key."""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                st.warning("Gemini API key not found. AI analysis features will be disabled.")
        except Exception as e:
            st.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def analyze_forecast_data(self, forecast_data, historical_data=None):
        """Generate intelligent insights from forecast data."""
        if not self.client:
            return None
        
        try:
            # Prepare data summary for analysis
            data_summary = self._prepare_forecast_summary(forecast_data, historical_data)
            
            system_prompt = """You are an expert dairy industry analyst with deep knowledge of market trends, 
            consumer behavior, and business operations. Analyze the provided forecast data and generate 
            actionable business insights. Focus on practical recommendations for dairy companies."""
            
            prompt = f"""
            Analyze this dairy product forecast data and provide comprehensive business insights:
            
            {data_summary}
            
            Please provide:
            1. Key trends and patterns you observe
            2. Business recommendations for production planning
            3. Risk factors and potential challenges
            4. Growth opportunities and market insights
            5. Overall confidence assessment of the forecast
            
            Format your response as a structured analysis that dairy executives can use for decision-making.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=ForecastInsights,
                ),
            )
            
            if response.text:
                return ForecastInsights(**json.loads(response.text))
            return None
            
        except Exception as e:
            st.error(f"Error analyzing forecast data: {str(e)}")
            return None
    
    def generate_competitive_analysis(self, company_data):
        """Generate competitive analysis insights."""
        if not self.client:
            return None
        
        try:
            competition_summary = self._prepare_competition_summary(company_data)
            
            system_prompt = """You are a strategic business analyst specializing in the dairy industry. 
            Analyze competitive positioning and provide strategic recommendations for market leadership."""
            
            prompt = f"""
            Analyze this competitive dairy market data and provide strategic insights:
            
            {competition_summary}
            
            Please provide:
            1. Market leader identification and reasoning
            2. Growth opportunities for each company
            3. Pricing strategy insights and recommendations
            4. Strategic recommendations for competitive advantage
            
            Focus on actionable strategies that companies can implement to improve market position.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=CompetitiveAnalysis,
                ),
            )
            
            if response.text:
                return CompetitiveAnalysis(**json.loads(response.text))
            return None
            
        except Exception as e:
            st.error(f"Error generating competitive analysis: {str(e)}")
            return None
    
    def generate_executive_summary(self, forecast_data, performance_metrics):
        """Generate executive summary report."""
        if not self.client:
            return "AI analysis unavailable - Gemini API key required"
        
        try:
            summary_data = {
                "forecast_summary": self._prepare_forecast_summary(forecast_data),
                "performance_metrics": performance_metrics
            }
            
            system_prompt = """You are a senior dairy industry consultant preparing an executive summary 
            for dairy company leadership. Create a comprehensive yet concise report that executives can 
            use for strategic decision-making."""
            
            prompt = f"""
            Create an executive summary report based on this dairy forecasting analysis:
            
            {json.dumps(summary_data, indent=2)}
            
            The report should include:
            1. Executive Overview (2-3 key points)
            2. Market Outlook and Trends
            3. Strategic Recommendations
            4. Risk Assessment
            5. Action Items for Management
            
            Write in professional business language suitable for C-level executives.
            Keep it concise but comprehensive.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Unable to generate summary"
            
        except Exception as e:
            return f"Error generating executive summary: {str(e)}"
    
    def analyze_seasonal_patterns(self, seasonal_data):
        """Analyze seasonal patterns and provide insights."""
        if not self.client:
            return None
        
        try:
            prompt = f"""
            Analyze these seasonal dairy consumption patterns and provide insights:
            
            {seasonal_data}
            
            Please explain:
            1. Key seasonal trends and their business implications
            2. Optimal production planning strategies for each season
            3. Marketing and promotional opportunities
            4. Inventory management recommendations
            5. Risk mitigation strategies for seasonal variations
            
            Provide practical, actionable recommendations for dairy companies.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text if response.text else "Unable to analyze seasonal patterns"
            
        except Exception as e:
            return f"Error analyzing seasonal patterns: {str(e)}"
    
    def _prepare_forecast_summary(self, forecast_data, historical_data=None):
        """Prepare data summary for AI analysis."""
        summary = {
            "forecast_period": "Next 30-90 days",
            "products_analyzed": [],
            "key_metrics": {},
            "trends": {}
        }
        
        if isinstance(forecast_data, dict):
            for product, data in forecast_data.items():
                if hasattr(data, 'tail'):  # DataFrame
                    summary["products_analyzed"].append(product)
                    summary["key_metrics"][product] = {
                        "avg_forecast": float(data['yhat'].mean()) if 'yhat' in data.columns else 0,
                        "trend_direction": "increasing" if data['yhat'].iloc[-1] > data['yhat'].iloc[0] else "decreasing",
                        "confidence_range": {
                            "lower": float(data['yhat_lower'].mean()) if 'yhat_lower' in data.columns else 0,
                            "upper": float(data['yhat_upper'].mean()) if 'yhat_upper' in data.columns else 0
                        }
                    }
        
        return summary
    
    def _prepare_competition_summary(self, company_data):
        """Prepare competitive data summary."""
        summary = {
            "companies": [],
            "market_metrics": {},
            "competitive_position": {}
        }
        
        if isinstance(company_data, dict):
            for company, metrics in company_data.items():
                summary["companies"].append(company)
                summary["market_metrics"][company] = metrics
        
        return summary