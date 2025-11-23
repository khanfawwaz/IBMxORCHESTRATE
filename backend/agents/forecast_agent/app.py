"""
Forecast Agent - ML-Powered Time Series Forecasting
Port 8004
Uses Prophet for demand forecasting with seasonality detection
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.shared.models import (
    ForecastRequest, ForecastResponse, DailyForecast,
    ForecastTrend, HealthCheckResponse, ErrorResponse
)
from backend.shared.database import get_db, get_sales_history, Session
from adk.agents.base_agent import BaseAgent, AgentTask, AgentResult, AgentStatus

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from loguru import logger
from typing import Optional
import os

# Initialize FastAPI app
app = FastAPI(
    title="Forecast Agent",
    description="ML-powered demand forecasting agent using Prophet",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model directory
MODEL_DIR = Path(__file__).parent.parent.parent / "ml" / "models"


class ForecastAgentImpl(BaseAgent):
    """Forecast Agent Implementation"""
    
    def __init__(self):
        super().__init__(
            agent_id="forecast_agent",
            agent_name="ML Forecaster",
            capabilities=["ml_prediction", "data_analysis"]
        )
        self.model_dir = MODEL_DIR
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate forecast request"""
        params = task.parameters
        
        if "sku" not in params or "location" not in params:
            return False
        
        forecast_days = params.get("forecast_days", 30)
        if forecast_days < 1 or forecast_days > 365:
            return False
        
        return True
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute forecasting task"""
        params = task.parameters
        
        sku = params["sku"]
        location = params["location"]
        forecast_days = params.get("forecast_days", 30)
        knowledge_context = params.get("knowledge_context")
        
        # Generate forecast
        forecast_response = await self.generate_forecast(
            sku, location, forecast_days, knowledge_context
        )
        
        return AgentResult(
            agent_id=self.agent_id,
            task_id=task.task_id,
            status=AgentStatus.SUCCESS,
            result=forecast_response.dict(),
            confidence=forecast_response.confidence,
            metadata={"model_used": forecast_response.model_used}
        )
    
    async def generate_forecast(
        self,
        sku: str,
        location: str,
        forecast_days: int,
        knowledge_context: Optional[str] = None
    ) -> ForecastResponse:
        """
        Generate demand forecast using Prophet model
        
        Args:
            sku: Product SKU
            location: Store location
            forecast_days: Number of days to forecast
            knowledge_context: Additional context for adjustment
            
        Returns:
            ForecastResponse with predictions
        """
        logger.info(f"Generating forecast for {sku} in {location} for {forecast_days} days")
        
        # Try to load trained model
        model_filename = f"prophet_{sku}_{location.replace(' ', '_')}.pkl"
        model_path = self.model_dir / model_filename
        
        if model_path.exists():
            # Use trained model
            model = joblib.load(model_path)
            model_used = "prophet_trained"
            logger.info(f"Using trained model: {model_filename}")
        else:
            # Use baseline model or create new one
            baseline_path = self.model_dir / "prophet_baseline.pkl"
            
            if baseline_path.exists():
                model = joblib.load(baseline_path)
                model_used = "prophet_baseline"
                logger.info("Using baseline model")
            else:
                # Train on-the-fly with available data
                model, model_used = await self._train_on_the_fly(sku, location)
        
        # Generate forecast
        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)
        
        # Get only future predictions
        future_forecast = forecast.tail(forecast_days)
        
        # Apply knowledge context adjustments
        if knowledge_context:
            future_forecast = self._apply_knowledge_context(
                future_forecast, knowledge_context
            )
        
        # Calculate total predicted demand
        total_demand = future_forecast['yhat'].sum()
        
        # Determine trend
        trend = self._determine_trend(future_forecast)
        
        # Calculate confidence
        confidence = self._calculate_confidence(future_forecast, model_used)
        
        # Build daily forecast
        daily_forecasts = []
        for _, row in future_forecast.iterrows():
            daily_forecasts.append(DailyForecast(
                date=row['ds'].strftime("%Y-%m-%d"),
                predicted_demand=max(0, row['yhat']),
                lower_bound=max(0, row['yhat_lower']),
                upper_bound=max(0, row['yhat_upper'])
            ))
        
        # Detect seasonality
        seasonality_detected = self._detect_seasonality(forecast)
        
        return ForecastResponse(
            sku=sku,
            location=location,
            total_predicted_demand=max(0, total_demand),
            trend=trend,
            confidence=confidence,
            daily_forecast=daily_forecasts,
            seasonality_detected=seasonality_detected,
            model_used=model_used
        )
    
    async def _train_on_the_fly(self, sku: str, location: str):
        """Train model on-the-fly with available data"""
        from prophet import Prophet
        from backend.shared.database import get_db
        
        logger.info(f"Training on-the-fly model for {sku} in {location}")
        
        # Get historical data
        with get_db() as db:
            sales = get_sales_history(db, sku=sku, location=location, limit=10000)
        
        if len(sales) < 14:
            # Not enough data, use synthetic baseline
            logger.warning(f"Insufficient data ({len(sales)} records), using synthetic baseline")
            return self._create_synthetic_model(), "synthetic"
        
        # Prepare data for Prophet
        df = pd.DataFrame([
            {
                'ds': sale.timestamp.date(),
                'y': sale.quantity
            }
            for sale in sales
        ])
        
        # Aggregate by date
        df = df.groupby('ds').agg({'y': 'sum'}).reset_index()
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Train Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        model.fit(df)
        
        return model, "prophet_on_the_fly"
    
    def _create_synthetic_model(self):
        """Create synthetic baseline model"""
        from prophet import Prophet
        
        # Create synthetic data with typical patterns
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=90),
            end=datetime.now(),
            freq='D'
        )
        
        # Generate synthetic sales with weekly pattern
        y = []
        for i, date in enumerate(dates):
            base = 50
            weekly_pattern = 20 * np.sin(2 * np.pi * i / 7)
            noise = np.random.normal(0, 5)
            y.append(max(0, base + weekly_pattern + noise))
        
        df = pd.DataFrame({'ds': dates, 'y': y})
        
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        
        model.fit(df)
        
        return model
    
    def _apply_knowledge_context(self, forecast_df: pd.DataFrame, context: str) -> pd.DataFrame:
        """Apply knowledge context to adjust forecast"""
        context_lower = context.lower()
        
        # Viral/trending products
        if any(word in context_lower for word in ['viral', 'trending', 'popular', 'tiktok', 'instagram']):
            logger.info("Applying viral trend adjustment (+100%)")
            forecast_df['yhat'] *= 2.0
            forecast_df['yhat_upper'] *= 2.5
        
        # Competitor impact
        elif any(word in context_lower for word in ['competitor', 'competition', 'rival']):
            logger.info("Applying competitor impact adjustment (-30%)")
            forecast_df['yhat'] *= 0.7
            forecast_df['yhat_lower'] *= 0.6
        
        # Supply issues
        elif any(word in context_lower for word in ['delay', 'shortage', 'unavailable']):
            logger.info("Applying supply constraint adjustment (-20%)")
            forecast_df['yhat'] *= 0.8
        
        # Promotion/sale
        elif any(word in context_lower for word in ['promotion', 'sale', 'discount', 'offer']):
            logger.info("Applying promotion adjustment (+50%)")
            forecast_df['yhat'] *= 1.5
            forecast_df['yhat_upper'] *= 1.8
        
        return forecast_df
    
    def _determine_trend(self, forecast_df: pd.DataFrame) -> ForecastTrend:
        """Determine trend direction"""
        trend_values = forecast_df['trend'].values
        
        if len(trend_values) < 2:
            return ForecastTrend.STABLE
        
        start_trend = trend_values[0]
        end_trend = trend_values[-1]
        
        change_pct = (end_trend - start_trend) / start_trend
        
        if change_pct > 0.05:
            return ForecastTrend.INCREASING
        elif change_pct < -0.05:
            return ForecastTrend.DECREASING
        else:
            return ForecastTrend.STABLE
    
    def _calculate_confidence(self, forecast_df: pd.DataFrame, model_used: str) -> float:
        """Calculate forecast confidence"""
        # Base confidence by model type
        base_confidence = {
            "prophet_trained": 0.85,
            "prophet_baseline": 0.65,
            "prophet_on_the_fly": 0.75,
            "synthetic": 0.50
        }.get(model_used, 0.60)
        
        # Adjust based on prediction interval width
        avg_interval_width = (
            forecast_df['yhat_upper'] - forecast_df['yhat_lower']
        ).mean()
        
        avg_prediction = forecast_df['yhat'].mean()
        
        if avg_prediction > 0:
            interval_ratio = avg_interval_width / avg_prediction
            # Narrower intervals = higher confidence
            confidence_adjustment = max(-0.2, min(0.2, (1 - interval_ratio) * 0.2))
        else:
            confidence_adjustment = 0
        
        final_confidence = base_confidence + confidence_adjustment
        
        return max(0.0, min(1.0, final_confidence))
    
    def _detect_seasonality(self, forecast_df: pd.DataFrame) -> bool:
        """Detect if seasonality is present"""
        if 'weekly' in forecast_df.columns or 'yearly' in forecast_df.columns:
            return True
        
        # Check if there's significant variation in trend
        if 'trend' in forecast_df.columns:
            trend_std = forecast_df['trend'].std()
            trend_mean = forecast_df['trend'].mean()
            
            if trend_mean > 0:
                cv = trend_std / trend_mean
                return cv > 0.1
        
        return False


# Initialize agent
forecast_agent = ForecastAgentImpl()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        agent_id="forecast_agent",
        version="1.0.0",
        dependencies={
            "prophet": "installed",
            "model_dir": str(MODEL_DIR),
            "models_available": len(list(MODEL_DIR.glob("*.pkl"))) if MODEL_DIR.exists() else 0
        }
    )


@app.post("/api/v1/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """
    Generate demand forecast
    
    Args:
        request: Forecast request with SKU, location, and forecast horizon
        
    Returns:
        Forecast response with predictions
    """
    try:
        forecast = await forecast_agent.generate_forecast(
            sku=request.sku,
            location=request.location,
            forecast_days=request.forecast_days,
            knowledge_context=request.knowledge_context
        )
        
        return forecast
        
    except Exception as e:
        logger.error(f"Forecast generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def get_status():
    """Get agent status"""
    return forecast_agent.get_status()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("FORECAST_AGENT_PORT", 8004))
    
    logger.info(f"Starting Forecast Agent on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
