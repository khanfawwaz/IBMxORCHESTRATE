"""
Gemini AI Integration
Provides AI-powered summaries and carbon footprint reduction tips
"""

import os
from typing import Dict, Any, Optional
from loguru import logger

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. AI features disabled.")


class GeminiAssistant:
    """Gemini AI assistant for warehouse analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("✓ Gemini AI initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                self.model = None
        else:
            logger.warning("Gemini API key not configured. Using fallback responses.")
    
    def check_warehouse_relevance(self, user_message: str) -> tuple[bool, str]:
        """
        Check if user message is warehouse/inventory related
        
        Returns:
            (is_relevant, response_message)
        """
        warehouse_keywords = [
            'warehouse', 'inventory', 'stock', 'supply', 'demand', 'forecast',
            'product', 'sku', 'shipment', 'order', 'logistics', 'distribution',
            'storage', 'fulfillment', 'procurement', 'vendor', 'supplier',
            'carbon', 'sustainability', 'risk', 'analysis', 'wh-', 'analyze'
        ]
        
        message_lower = user_message.lower()
        
        # Check if message contains warehouse-related keywords
        is_relevant = any(keyword in message_lower for keyword in warehouse_keywords)
        
        if not is_relevant:
            return False, """
                I'm specifically designed to help with warehouse and inventory management. 
                I can assist you with:
                
                📦 Inventory forecasting and demand prediction
                🚚 Supply chain analysis and optimization
                ⚠️ Risk assessment for stock levels
                🌱 Carbon footprint and sustainability metrics
                📊 Product performance analysis
                
                Please ask me something related to warehouse operations!
            """
        
        return True, ""
    
    async def generate_analysis_summary(
        self,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Generate AI-powered summary of the complete analysis
        
        Args:
            analysis_data: Complete analysis response data
            
        Returns:
            Human-friendly summary
        """
        if not self.model:
            return self._fallback_summary(analysis_data)
        
        try:
            forecast = analysis_data.get('forecast', {})
            supply = analysis_data.get('supply', {})
            risk = analysis_data.get('risk', {})
            sustainability = analysis_data.get('sustainability', {})
            
            prompt = f"""
You are a warehouse management AI assistant. Provide a concise, actionable summary of this inventory analysis.

**Product:** {analysis_data.get('sku', 'Unknown')}
**Location:** {analysis_data.get('location', 'Unknown')}

**Forecast Data:**
- Predicted Demand: {forecast.get('total_predicted_demand', 0):.0f} units (30 days)
- Trend: {forecast.get('trend', 'stable')}
- Confidence: {forecast.get('confidence', 0) * 100:.0f}%

**Supply Chain:**
- Supplier: {supply.get('supplier', 'Unknown')}
- Lead Time: {supply.get('lead_time_days', 0)} days
- Current Stock: {supply.get('current_stock', 0)} units

**Risk Assessment:**
- Risk Level: {risk.get('risk_level', 'unknown')}
- Risk Score: {risk.get('risk_score', 0) * 100:.0f}%

**Sustainability:**
- Carbon Footprint: {sustainability.get('carbon_footprint_kg', 0):.0f} kg CO₂
- Sustainability Score: {sustainability.get('sustainability_score', 0):.0f}/100

**Recommendation:** {analysis_data.get('recommendation', 'No recommendation')}

Provide a 3-4 sentence executive summary that:
1. Highlights the key finding
2. Mentions the main risk or opportunity
3. Gives a clear action recommendation

Keep it professional but conversational. Use emojis sparingly (max 2).
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini summary generation failed: {str(e)}")
            return self._fallback_summary(analysis_data)
    
    async def generate_carbon_reduction_tips(
        self,
        sku: str,
        quantity: int,
        carbon_footprint: float,
        sustainability_score: float,
        supply_data: Dict[str, Any]
    ) -> str:
        """
        Generate personalized carbon footprint reduction tips
        
        Args:
            sku: Product SKU
            quantity: Order quantity
            carbon_footprint: Current carbon footprint in kg CO₂
            sustainability_score: Current sustainability score (0-100)
            supply_data: Supply chain information
            
        Returns:
            Personalized tips for reducing carbon footprint
        """
        if not self.model:
            return self._fallback_carbon_tips(carbon_footprint, sustainability_score)
        
        try:
            prompt = f"""
You are a sustainability expert for warehouse operations. Analyze this order and provide specific, actionable tips to reduce carbon emissions.

**Order Details:**
- Product SKU: {sku}
- Quantity: {quantity} units
- Current Carbon Footprint: {carbon_footprint:.1f} kg CO₂
- Sustainability Score: {sustainability_score:.0f}/100
- Supplier: {supply_data.get('supplier', 'Unknown')}
- Lead Time: {supply_data.get('lead_time_days', 0)} days

**Context:**
Consider real warehouse scenarios like:
- Packaging optimization (e.g., 500 jackets but only 200 proper-sized boxes → using oversized boxes wastes materials and increases shipping emissions)
- Consolidation opportunities
- Local vs. distant suppliers
- Transportation mode optimization
- Inventory holding costs

Provide 4-5 specific, actionable tips that:
1. Address packaging efficiency
2. Consider transportation optimization
3. Suggest supplier/sourcing improvements
4. Recommend inventory management strategies
5. Include estimated CO₂ savings where possible

Format as a numbered list. Be specific and practical. Use real numbers when estimating savings.
"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini carbon tips generation failed: {str(e)}")
            return self._fallback_carbon_tips(carbon_footprint, sustainability_score)
    
    def _fallback_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Fallback summary when Gemini is unavailable"""
        forecast = analysis_data.get('forecast', {})
        risk = analysis_data.get('risk', {})
        
        demand = forecast.get('total_predicted_demand', 0)
        trend = forecast.get('trend', 'stable')
        risk_level = risk.get('risk_level', 'unknown')
        
        return f"""
📊 **Analysis Summary:**

Forecasted demand of {demand:.0f} units over 30 days with a {trend} trend. 
Risk level is {risk_level}, requiring {"immediate attention" if risk_level in ['high', 'critical'] else "standard monitoring"}. 
{analysis_data.get('recommendation', 'Review the detailed metrics below for full insights.')}
        """.strip()
    
    def _fallback_carbon_tips(self, carbon_footprint: float, sustainability_score: float) -> str:
        """Fallback carbon tips when Gemini is unavailable"""
        tips = [
            f"**Optimize Packaging:** Right-size your packaging to reduce material waste and shipping volume. Estimated savings: {carbon_footprint * 0.15:.1f} kg CO₂",
            f"**Consolidate Shipments:** Combine orders to reduce transportation trips. Potential reduction: {carbon_footprint * 0.20:.1f} kg CO₂",
            "**Local Sourcing:** Consider suppliers closer to your warehouse to reduce transportation emissions",
            "**Eco-Friendly Materials:** Switch to recyclable or biodegradable packaging materials",
            "**Optimize Inventory:** Reduce excess stock to minimize storage energy consumption"
        ]
        
        return "\n\n".join(f"{i+1}. {tip}" for i, tip in enumerate(tips))


# Global instance
_gemini_assistant = None

def get_gemini_assistant() -> GeminiAssistant:
    """Get or create Gemini assistant instance"""
    global _gemini_assistant
    if _gemini_assistant is None:
        _gemini_assistant = GeminiAssistant()
    return _gemini_assistant
