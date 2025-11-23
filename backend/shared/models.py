"""
Shared Data Models and Schemas
Pydantic models for request/response validation across all agents
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class TrendSource(str, Enum):
    """Social media trend sources"""
    GOOGLE_TRENDS = "google_trends"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"


class ForecastTrend(str, Enum):
    """Forecast trend direction"""
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupplyFeasibility(str, Enum):
    """Supply chain feasibility"""
    IMMEDIATE = "immediate"
    WITHIN_WEEK = "within_week"
    WITHIN_MONTH = "within_month"
    DELAYED = "delayed"
    UNAVAILABLE = "unavailable"


# ============================================================================
# Request Models
# ============================================================================

class AnalysisRequest(BaseModel):
    """Main analysis request"""
    sku: str = Field(..., description="Product SKU", example="WH-FP-0001")
    location: str = Field(..., description="Store location", example="New York")
    forecast_days: int = Field(default=30, ge=1, le=365, description="Forecast horizon in days")
    quantity: int = Field(default=100, ge=1, description="Quantity to analyze")
    knowledge_context: Optional[str] = Field(
        None,
        description="Additional context (e.g., 'Product trending on social media')"
    )
    company_id: Optional[str] = Field(
        None,
        description="Company ID for multi-tenant support"
    )


class SocialCollectRequest(BaseModel):
    """Social trend collection request"""
    sku: str = Field(..., description="Product SKU")
    location: str = Field(..., description="Store location")
    platforms: Optional[List[TrendSource]] = Field(
        None,
        description="Specific platforms to check"
    )


class ForecastRequest(BaseModel):
    """Forecasting request"""
    sku: str = Field(..., description="Product SKU")
    location: str = Field(..., description="Store location")
    forecast_days: int = Field(default=30, ge=1, le=365)
    knowledge_context: Optional[str] = None


class SupplyCheckRequest(BaseModel):
    """Supply chain check request"""
    sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., description="Required quantity")
    location: str = Field(..., description="Delivery location")


class RiskAnalysisRequest(BaseModel):
    """Risk analysis request"""
    forecast_data: Dict[str, Any] = Field(..., description="Forecast results")
    supply_data: Dict[str, Any] = Field(..., description="Supply chain data")
    social_signals: List[Dict[str, Any]] = Field(default_factory=list)


class SustainabilityRequest(BaseModel):
    """Sustainability calculation request"""
    sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., description="Quantity")
    origin_location: str = Field(..., description="Origin location")
    destination_location: str = Field(..., description="Destination location")


# ============================================================================
# Response Models
# ============================================================================

class SocialSignal(BaseModel):
    """Individual social media signal"""
    source: TrendSource = Field(..., description="Signal source")
    metric: str = Field(..., description="Metric name")
    engagement_value: float = Field(..., ge=0.0, le=1.0, description="Engagement score (0-1)")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="Reliability score (0-1)")
    mentions: Optional[int] = Field(None, description="Number of mentions")
    sentiment: Optional[str] = Field(None, description="Sentiment (positive/neutral/negative)")
    timestamp: datetime = Field(default_factory=datetime.now)


class SocialCollectResponse(BaseModel):
    """Social trend collection response"""
    sku: str
    location: str
    signals: List[SocialSignal]
    summary: str = Field(..., description="Human-readable summary")
    overall_engagement: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class DailyForecast(BaseModel):
    """Daily forecast data point"""
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    predicted_demand: float = Field(..., description="Predicted quantity")
    lower_bound: float = Field(..., description="Lower confidence bound")
    upper_bound: float = Field(..., description="Upper confidence bound")


class ForecastResponse(BaseModel):
    """Forecasting response"""
    sku: str
    location: str
    total_predicted_demand: float = Field(..., description="Total predicted demand")
    trend: ForecastTrend = Field(..., description="Trend direction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")
    daily_forecast: List[DailyForecast] = Field(default_factory=list)
    seasonality_detected: bool = Field(default=False)
    model_used: str = Field(default="prophet")
    timestamp: datetime = Field(default_factory=datetime.now)


class SupplyCheckResponse(BaseModel):
    """Supply chain check response"""
    sku: str
    supplier: str = Field(..., description="Supplier name")
    lead_time_days: int = Field(..., description="Lead time in days")
    current_stock: int = Field(..., description="Current stock level")
    availability: str = Field(..., description="Availability status")
    feasibility: SupplyFeasibility = Field(..., description="Fulfillment feasibility")
    unit_cost: float = Field(..., description="Unit cost")
    minimum_order_quantity: int = Field(..., description="Minimum order quantity")
    timestamp: datetime = Field(default_factory=datetime.now)


class RiskFactor(BaseModel):
    """Individual risk factor"""
    factor: str = Field(..., description="Risk factor description")
    impact: float = Field(..., ge=0.0, le=1.0, description="Impact score")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy")


class RiskAnalysisResponse(BaseModel):
    """Risk analysis response"""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    factors: List[RiskFactor] = Field(default_factory=list)
    recommendation: str = Field(..., description="Risk-based recommendation")
    timestamp: datetime = Field(default_factory=datetime.now)


class SustainabilityResponse(BaseModel):
    """Sustainability analysis response"""
    carbon_footprint_kg: float = Field(..., description="Carbon footprint in kg CO2")
    sustainability_score: float = Field(..., ge=0.0, le=100.0, description="Sustainability score (0-100)")
    transport_emissions: float = Field(..., description="Transport emissions in kg CO2")
    manufacturing_emissions: float = Field(..., description="Manufacturing emissions in kg CO2")
    packaging_emissions: float = Field(..., description="Packaging emissions in kg CO2")
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class ExplanationFactor(BaseModel):
    """Explanation factor"""
    factor: str = Field(..., description="Factor description")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score")
    impact: str = Field(..., description="Impact description")


class XAIResponse(BaseModel):
    """XAI explanation response"""
    top_factors: List[ExplanationFactor] = Field(..., description="Top influencing factors")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Explanation confidence")
    summary: str = Field(..., description="Human-readable summary")
    methodology: str = Field(default="SHAP-inspired", description="Explanation methodology")
    timestamp: datetime = Field(default_factory=datetime.now)


class UnifiedAnalysisResponse(BaseModel):
    """Complete unified analysis response"""
    sku: str
    location: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Component results
    social_signals: List[SocialSignal] = Field(default_factory=list)
    social_summary: str = Field(default="No social data available")
    
    forecast: ForecastResponse
    supply: SupplyCheckResponse
    risk: RiskAnalysisResponse
    sustainability: SustainabilityResponse
    explanation: XAIResponse
    
    # Overall analysis
    recommendation: str = Field(..., description="Final recommendation")
    action_items: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    executive_summary: Optional[str] = Field(None, description="AI-generated executive summary")


# ============================================================================
# Database Models
# ============================================================================

class ProductDB(BaseModel):
    """Product database model"""
    sku: str
    name: str
    category: str
    subcategory: str
    brand: str
    base_price: float
    unit: str
    perishable: bool
    seasonality_factor: float


class SalesRecordDB(BaseModel):
    """Sales record database model"""
    id: Optional[int] = None
    timestamp: datetime
    sku: str
    product_name: str
    category: str
    location: str
    quantity: int
    unit_price: float
    revenue: float


class SupplyChainDB(BaseModel):
    """Supply chain database model"""
    sku: str
    product_name: str
    supplier: str
    lead_time_days: int
    current_stock: int
    reorder_point: int
    supplier_reliability: float
    unit_cost: float
    minimum_order_quantity: int


# ============================================================================
# Utility Models
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    agent_id: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    dependencies: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
