"""
Unified Orchestrator - IBM watsonx Orchestrate ADK Integration
Port 9000
Coordinates all agents to provide complete analysis in a single request
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.shared.models import (
    AnalysisRequest, UnifiedAnalysisResponse,
    ForecastResponse, SupplyCheckResponse, RiskAnalysisResponse,
    SustainabilityResponse, XAIResponse, SocialSignal,
    ExplanationFactor, RiskFactor, RiskLevel, ForecastTrend,
    HealthCheckResponse
)
from adk.workflows.orchestration_engine import (
    AgentOrchestrator, create_complete_analysis_workflow
)
from adk.config.orchestrator_config import get_orchestrator_config

from loguru import logger
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import os
import httpx
from pydantic import BaseModel

# Import Gemini helper
from backend.shared.gemini_helper import get_gemini_assistant

app = FastAPI(
    title="Unified Orchestrator",
    description="IBM watsonx Orchestrate ADK - Complete Inventory Analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator_config = get_orchestrator_config()
orchestrator = AgentOrchestrator(orchestrator_config)

# Register complete analysis workflow
complete_workflow = create_complete_analysis_workflow()
orchestrator.register_workflow(complete_workflow)


class UnifiedOrchestratorService:
    """Unified orchestrator service implementation"""
    
    def __init__(self):
        self.base_url = "http://localhost"
        self.timeout = 30.0
    
    async def analyze(self, request: AnalysisRequest) -> UnifiedAnalysisResponse:
        """
        Perform complete unified analysis
        
        Args:
            request: Analysis request
            
        Returns:
            Complete analysis response
        """
        logger.info(f"Starting unified analysis for {request.sku} in {request.location}")
        
        # Execute all components
        try:
            # 1. Collect social signals (optional, may fail)
            social_signals, social_summary = await self._collect_social_signals(
                request.sku, request.location
            )
            
            # 2. Generate forecast (critical)
            forecast = await self._generate_forecast(
                request.sku, request.location, request.forecast_days,
                request.knowledge_context
            )
            
            # 3. Check supply chain (critical)
            supply = await self._check_supply(
                request.sku,
                int(forecast.total_predicted_demand),
                request.location
            )
            
            # 4. Analyze risk
            risk = await self._analyze_risk(forecast, supply, social_signals)
            
            # 5. Calculate sustainability
            sustainability = await self._calculate_sustainability(
                request.sku, request.quantity, request.location
            )
            
            # 6. Generate explanation
            explanation = await self._generate_explanation(forecast, risk, social_signals)
            
            # 7. Generate recommendation
            recommendation, action_items = self._generate_recommendation(
                forecast, supply, risk, sustainability
            )
            
            # 8. Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                forecast, supply, risk, explanation
            )
            
            # 9. Generate executive summary (optional)
            executive_summary = self._generate_executive_summary(
                forecast, supply, risk, sustainability, recommendation
            )
            
            return UnifiedAnalysisResponse(
                sku=request.sku,
                location=request.location,
                social_signals=social_signals,
                social_summary=social_summary,
                forecast=forecast,
                supply=supply,
                risk=risk,
                sustainability=sustainability,
                explanation=explanation,
                recommendation=recommendation,
                action_items=action_items,
                overall_confidence=overall_confidence,
                executive_summary=executive_summary
            )
            
        except Exception as e:
            logger.error(f"Unified analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _collect_social_signals(
        self, sku: str, location: str
    ) -> tuple[List[SocialSignal], str]:
        """Collect social media signals (simulated for now)"""
        try:
            # In production, this would call the social agent
            # For now, return simulated data
            import random
            
            signals = [
                SocialSignal(
                    source="google_trends",
                    metric="search_interest",
                    engagement_value=random.uniform(0.5, 0.9),
                    reliability_score=0.95,
                    mentions=random.randint(100, 5000),
                    sentiment="positive"
                ),
                SocialSignal(
                    source="reddit",
                    metric="discussion_volume",
                    engagement_value=random.uniform(0.3, 0.7),
                    reliability_score=0.85,
                    mentions=random.randint(50, 500),
                    sentiment="neutral"
                )
            ]
            
            avg_engagement = sum(s.engagement_value for s in signals) / len(signals)
            
            if avg_engagement > 0.7:
                summary = f"High social activity ({avg_engagement:.0%} engagement)"
            elif avg_engagement > 0.4:
                summary = f"Moderate social activity ({avg_engagement:.0%} engagement)"
            else:
                summary = f"Low social activity ({avg_engagement:.0%} engagement)"
            
            return signals, summary
            
        except Exception as e:
            logger.warning(f"Social signal collection failed: {str(e)}")
            return [], "No social data available"
    
    async def _generate_forecast(
        self, sku: str, location: str, forecast_days: int,
        knowledge_context: str = None
    ) -> ForecastResponse:
        """Generate forecast using forecast agent"""
        try:
            # Call forecast agent
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}:8004/api/v1/forecast",
                    json={
                        "sku": sku,
                        "location": location,
                        "forecast_days": forecast_days,
                        "knowledge_context": knowledge_context
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ForecastResponse(**data)
                else:
                    raise Exception(f"Forecast agent returned {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Forecast generation failed: {str(e)}")
            # Return fallback forecast
            return self._create_fallback_forecast(sku, location, forecast_days)
    
    def _create_fallback_forecast(
        self, sku: str, location: str, forecast_days: int
    ) -> ForecastResponse:
        """Create fallback forecast when agent fails"""
        import random
        
        daily_avg = random.randint(50, 150)
        total_demand = daily_avg * forecast_days
        
        return ForecastResponse(
            sku=sku,
            location=location,
            total_predicted_demand=total_demand,
            trend=ForecastTrend.STABLE,
            confidence=0.5,
            daily_forecast=[],
            seasonality_detected=False,
            model_used="fallback"
        )
    
    async def _check_supply(
        self, sku: str, quantity: int, location: str
    ) -> SupplyCheckResponse:
        """Check supply chain using supply agent"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}:8005/api/v1/check",
                    json={
                        "sku": sku,
                        "quantity": quantity,
                        "location": location
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return SupplyCheckResponse(**data)
                else:
                    raise Exception(f"Supply agent returned {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Supply check failed: {str(e)}")
            return self._create_fallback_supply(sku)
    
    def _create_fallback_supply(self, sku: str) -> SupplyCheckResponse:
        """Create fallback supply response"""
        from backend.shared.models import SupplyFeasibility
        
        return SupplyCheckResponse(
            sku=sku,
            supplier="Unknown Supplier",
            lead_time_days=14,
            current_stock=500,
            availability="unknown",
            feasibility=SupplyFeasibility.WITHIN_MONTH,
            unit_cost=10.0,
            minimum_order_quantity=50
        )
    
    async def _analyze_risk(
        self,
        forecast: ForecastResponse,
        supply: SupplyCheckResponse,
        social_signals: List[SocialSignal]
    ) -> RiskAnalysisResponse:
        """Analyze risk factors"""
        risk_score = 0.0
        factors = []
        
        # Forecast trend risk
        if forecast.trend == ForecastTrend.INCREASING:
            risk_score += 0.15
            factors.append(RiskFactor(
                factor="Increasing demand trend",
                impact=0.15,
                mitigation="Increase safety stock"
            ))
        elif forecast.trend == ForecastTrend.DECREASING:
            risk_score += 0.10
            factors.append(RiskFactor(
                factor="Decreasing demand trend",
                impact=0.10,
                mitigation="Reduce order quantity"
            ))
        
        # Supply chain risk
        if supply.lead_time_days > 21:
            risk_score += 0.25
            factors.append(RiskFactor(
                factor=f"Long lead time ({supply.lead_time_days} days)",
                impact=0.25,
                mitigation="Find alternative suppliers"
            ))
        
        if supply.availability == "out_of_stock":
            risk_score += 0.30
            factors.append(RiskFactor(
                factor="Out of stock",
                impact=0.30,
                mitigation="Expedite delivery or find alternatives"
            ))
        
        # Social media volatility risk
        if social_signals:
            avg_engagement = sum(s.engagement_value for s in social_signals) / len(social_signals)
            if avg_engagement > 0.8:
                risk_score += 0.20
                factors.append(RiskFactor(
                    factor="High social media volatility",
                    impact=0.20,
                    mitigation="Monitor trends closely"
                ))
        
        # Forecast confidence risk
        if forecast.confidence < 0.6:
            risk_score += 0.15
            factors.append(RiskFactor(
                factor="Low forecast confidence",
                impact=0.15,
                mitigation="Gather more historical data"
            ))
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.6:
            risk_level = RiskLevel.MEDIUM
        elif risk_score < 0.8:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        # Generate recommendation
        if risk_level == RiskLevel.LOW:
            recommendation = "✅ Low risk - Proceed with standard ordering"
        elif risk_level == RiskLevel.MEDIUM:
            recommendation = "⚠️ Medium risk - Proceed with caution and monitoring"
        elif risk_level == RiskLevel.HIGH:
            recommendation = "🔴 High risk - Review carefully before proceeding"
        else:
            recommendation = "🛑 Critical risk - Do not proceed without mitigation"
        
        return RiskAnalysisResponse(
            risk_score=min(1.0, risk_score),
            risk_level=risk_level,
            factors=factors[:5],  # Top 5 factors
            recommendation=recommendation
        )
    
    async def _calculate_sustainability(
        self, sku: str, quantity: int, location: str
    ) -> SustainabilityResponse:
        """Calculate sustainability metrics"""
        import random
        
        # Simplified sustainability calculation
        # In production, this would use real data
        
        # Transport emissions (kg CO2 per unit * distance factor)
        distance_factor = random.uniform(0.5, 2.0)
        transport_emissions = quantity * distance_factor * 0.1
        
        # Manufacturing emissions
        manufacturing_emissions = quantity * 2.5
        
        # Packaging emissions
        packaging_emissions = quantity * 0.5
        
        # Total carbon footprint
        carbon_footprint = transport_emissions + manufacturing_emissions + packaging_emissions
        
        # Calculate sustainability score (0-100)
        base_score = 50
        
        # Bonuses
        if distance_factor < 1.0:  # Local sourcing
            base_score += 15
        
        if random.random() > 0.5:  # Recyclable packaging
            base_score += 10
        
        if random.random() > 0.7:  # Renewable energy
            base_score += 15
        
        sustainability_score = min(100, base_score)
        
        # Recommendations
        recommendations = []
        if distance_factor > 1.5:
            recommendations.append("Consider local suppliers to reduce transport emissions")
        if packaging_emissions > carbon_footprint * 0.2:
            recommendations.append("Use recyclable or biodegradable packaging")
        if sustainability_score < 60:
            recommendations.append("Explore renewable energy options for manufacturing")
        
        return SustainabilityResponse(
            carbon_footprint_kg=round(carbon_footprint, 2),
            sustainability_score=round(sustainability_score, 1),
            transport_emissions=round(transport_emissions, 2),
            manufacturing_emissions=round(manufacturing_emissions, 2),
            packaging_emissions=round(packaging_emissions, 2),
            recommendations=recommendations
        )
    
    async def _generate_explanation(
        self,
        forecast: ForecastResponse,
        risk: RiskAnalysisResponse,
        social_signals: List[SocialSignal]
    ) -> XAIResponse:
        """Generate XAI explanation"""
        factors = []
        
        # Forecast trend factor
        if forecast.trend == ForecastTrend.INCREASING:
            factors.append(ExplanationFactor(
                factor="Historical upward trend",
                importance=0.35,
                impact="Demand expected to grow based on past patterns"
            ))
        elif forecast.trend == ForecastTrend.DECREASING:
            factors.append(ExplanationFactor(
                factor="Historical downward trend",
                importance=0.35,
                impact="Demand expected to decline based on past patterns"
            ))
        else:
            factors.append(ExplanationFactor(
                factor="Stable historical trend",
                importance=0.30,
                impact="Demand expected to remain consistent"
            ))
        
        # Social media factor
        if social_signals:
            avg_engagement = sum(s.engagement_value for s in social_signals) / len(social_signals)
            if avg_engagement > 0.6:
                factors.append(ExplanationFactor(
                    factor="High social media engagement",
                    importance=0.25,
                    impact="Product gaining attention on social platforms"
                ))
        
        # Seasonality factor
        if forecast.seasonality_detected:
            factors.append(ExplanationFactor(
                factor="Seasonal patterns detected",
                importance=0.20,
                impact="Demand varies by time of year/week"
            ))
        
        # Confidence factor
        factors.append(ExplanationFactor(
            factor=f"Model confidence: {forecast.confidence:.0%}",
            importance=0.15,
            impact=f"Prediction reliability is {forecast.confidence:.0%}"
        ))
        
        # Sort by importance
        factors.sort(key=lambda x: x.importance, reverse=True)
        
        # Generate summary
        top_factor = factors[0] if factors else None
        if top_factor:
            summary = f"Forecast primarily driven by {top_factor.factor.lower()} ({top_factor.importance:.0%} importance)"
        else:
            summary = "Forecast based on historical patterns"
        
        return XAIResponse(
            top_factors=factors[:5],
            confidence=forecast.confidence,
            summary=summary
        )
    
    def _generate_recommendation(
        self,
        forecast: ForecastResponse,
        supply: SupplyCheckResponse,
        risk: RiskAnalysisResponse,
        sustainability: SustainabilityResponse
    ) -> tuple[str, List[str]]:
        """Generate final recommendation and action items"""
        
        # Determine order quantity
        predicted_demand = int(forecast.total_predicted_demand)
        
        # Adjust based on risk
        if risk.risk_level == RiskLevel.HIGH or risk.risk_level == RiskLevel.CRITICAL:
            order_quantity = int(predicted_demand * 0.7)  # Conservative
        elif risk.risk_level == RiskLevel.MEDIUM:
            order_quantity = int(predicted_demand * 0.85)  # Slightly conservative
        else:
            order_quantity = predicted_demand  # Full amount
        
        # Ensure minimum order quantity
        if order_quantity < supply.minimum_order_quantity:
            order_quantity = supply.minimum_order_quantity
        
        # Generate recommendation
        if risk.risk_level == RiskLevel.LOW:
            recommendation = f"✅ PROCEED: Order {order_quantity} units. Low risk, favorable conditions."
        elif risk.risk_level == RiskLevel.MEDIUM:
            recommendation = f"⚠️ CAUTION: Order {order_quantity} units initially. Monitor {risk.factors[0].factor.lower()}."
        elif risk.risk_level == RiskLevel.HIGH:
            recommendation = f"🔴 HIGH RISK: Consider ordering {order_quantity} units. Address {risk.factors[0].factor.lower()} first."
        else:
            recommendation = f"🛑 HOLD: Critical risk detected. Review {risk.factors[0].factor.lower()} before ordering."
        
        # Generate action items
        action_items = [
            f"Prepare for {predicted_demand} units over {forecast.total_predicted_demand / predicted_demand if predicted_demand > 0 else 30:.0f} days",
            f"Lead time: {supply.lead_time_days} days from {supply.supplier}",
        ]
        
        if forecast.trend == ForecastTrend.INCREASING:
            action_items.append("Monitor increasing demand trend closely")
        elif forecast.trend == ForecastTrend.DECREASING:
            action_items.append("Review pricing strategy due to decreasing trend")
        
        if sustainability.sustainability_score < 60:
            action_items.append("Improve sustainability score through green initiatives")
        
        if risk.factors:
            action_items.append(f"Mitigate risk: {risk.factors[0].mitigation}")
        
        return recommendation, action_items[:5]
    
    def _calculate_overall_confidence(
        self,
        forecast: ForecastResponse,
        supply: SupplyCheckResponse,
        risk: RiskAnalysisResponse,
        explanation: XAIResponse
    ) -> float:
        """Calculate overall confidence score"""
        
        # Weighted average of component confidences
        weights = {
            "forecast": 0.40,
            "supply": 0.20,
            "risk": 0.25,
            "explanation": 0.15
        }
        
        # Supply confidence (based on availability)
        supply_confidence = 0.9 if supply.availability == "in_stock" else 0.6
        
        # Risk confidence (inverse of risk score)
        risk_confidence = 1.0 - risk.risk_score
        
        overall = (
            forecast.confidence * weights["forecast"] +
            supply_confidence * weights["supply"] +
            risk_confidence * weights["risk"] +
            explanation.confidence * weights["explanation"]
        )
        
        return round(overall, 2)
    
    def _generate_executive_summary(
        self,
        forecast: ForecastResponse,
        supply: SupplyCheckResponse,
        risk: RiskAnalysisResponse,
        sustainability: SustainabilityResponse,
        recommendation: str
    ) -> str:
        """Generate executive summary"""
        
        summary = f"""**EXECUTIVE SUMMARY**

**Demand Forecast**: {forecast.total_predicted_demand:.0f} units ({forecast.trend.value} trend)
**Supply Status**: {supply.availability} ({supply.lead_time_days} days lead time)
**Risk Level**: {risk.risk_level.value.upper()} ({risk.risk_score:.0%} risk score)
**Sustainability**: {sustainability.sustainability_score:.0f}/100 ({sustainability.carbon_footprint_kg:.0f} kg CO2)

**Recommendation**: {recommendation}

**Key Insights**:
• Forecast confidence: {forecast.confidence:.0%}
• Primary risk: {risk.factors[0].factor if risk.factors else 'None identified'}
• Supplier: {supply.supplier}
"""
        
        return summary


# Initialize service
orchestrator_service = UnifiedOrchestratorService()


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check"""
    return HealthCheckResponse(
        status="healthy",
        agent_id="unified_orchestrator",
        version="1.0.0",
        dependencies={
            "forecast_agent": "http://localhost:8004",
            "supply_agent": "http://localhost:8005"
        }
    )


@app.post("/api/v1/analyze", response_model=UnifiedAnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Complete unified analysis
    
    Coordinates all agents to provide comprehensive inventory analysis
    """
    try:
        return await orchestrator_service.analyze(request)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "orchestrator": "running",
        "workflows_registered": len(orchestrator.workflows),
        "agents_registered": len(orchestrator.agents)
    }


# ============================================================================
# Chatbot Endpoint with Gemini AI
# ============================================================================

class ChatbotRequest(BaseModel):
    """Chatbot request model"""
    message: str
    sku: Optional[str] = None
    location: Optional[str] = None


class ChatbotResponse(BaseModel):
    """Enhanced chatbot response with Gemini AI"""
    is_relevant: bool
    response_message: str
    analysis_data: Optional[UnifiedAnalysisResponse] = None
    ai_summary: Optional[str] = None
    carbon_tips: Optional[str] = None


@app.post("/api/v1/chat", response_model=ChatbotResponse)
async def chatbot(request: ChatbotRequest):
    """
    Chatbot endpoint with Gemini AI integration
    
    Features:
    - Guardrails: Only responds to warehouse-related queries
    - AI Summary: Gemini-powered analysis summary
    - Carbon Tips: Personalized carbon reduction recommendations
    """
    try:
        gemini = get_gemini_assistant()
        
        # Check if query is warehouse-related (guardrail)
        is_relevant, guard_message = gemini.check_warehouse_relevance(request.message)
        
        if not is_relevant:
            return ChatbotResponse(
                is_relevant=False,
                response_message=guard_message,
                analysis_data=None,
                ai_summary=None,
                carbon_tips=None
            )
        
        # Extract SKU and location from message if not provided
        if not request.sku:
            import re
            sku_match = re.search(r'WH-[A-Z]{2}-\d{4}', request.message, re.IGNORECASE)
            request.sku = sku_match.group(0).upper() if sku_match else 'WH-FP-0001'
        
        if not request.location:
            locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
            request.location = next(
                (loc for loc in locations if loc.lower() in request.message.lower()),
                'New York'
            )
        
        # Perform analysis
        analysis_request = AnalysisRequest(
            sku=request.sku,
            location=request.location,
            forecast_days=30,
            quantity=100
        )
        
        analysis_data = await orchestrator_service.analyze(analysis_request)
        
        # Generate AI-powered summary
        ai_summary = await gemini.generate_analysis_summary(analysis_data.dict())
        
        # Generate carbon reduction tips
        carbon_tips = await gemini.generate_carbon_reduction_tips(
            sku=request.sku,
            quantity=100,
            carbon_footprint=analysis_data.sustainability.carbon_footprint_kg,
            sustainability_score=analysis_data.sustainability.sustainability_score,
            supply_data=analysis_data.supply.dict()
        )
        
        return ChatbotResponse(
            is_relevant=True,
            response_message=f"Analysis complete for {request.sku} in {request.location}",
            analysis_data=analysis_data,
            ai_summary=ai_summary,
            carbon_tips=carbon_tips
        )
        
    except Exception as e:
        logger.error(f"Chatbot request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("ORCHESTRATOR_PORT", 9000))
    logger.info(f"Starting Unified Orchestrator on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
