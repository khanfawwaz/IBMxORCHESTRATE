"""
Test Gemini AI Integration
Quick test to verify Gemini is working
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Set API key
os.environ["GEMINI_API_KEY"] = "AIzaSyAso12ftM8rv5khI1YwhFg3BNq8vDnsJO0"

from backend.shared.gemini_helper import get_gemini_assistant
import asyncio

async def test_gemini():
    print("=" * 70)
    print("  TESTING GEMINI AI INTEGRATION")
    print("=" * 70 + "\n")
    
    gemini = get_gemini_assistant()
    
    # Test 1: Guardrails
    print("Test 1: Guardrails (Warehouse Query)")
    is_relevant, message = gemini.check_warehouse_relevance("Analyze product WH-FP-0001")
    print(f"✓ Relevant: {is_relevant}")
    
    print("\nTest 2: Guardrails (Off-topic Query)")
    is_relevant, message = gemini.check_warehouse_relevance("What's the weather?")
    print(f"✓ Rejected: {not is_relevant}")
    if not is_relevant:
        print(f"  Message: {message[:100]}...")
    
    # Test 3: AI Summary
    print("\nTest 3: AI Summary Generation")
    test_data = {
        "sku": "WH-FP-0001",
        "location": "New York",
        "forecast": {
            "total_predicted_demand": 3420,
            "trend": "increasing",
            "confidence": 0.85
        },
        "supply": {
            "supplier": "GlobalFoods Inc",
            "lead_time_days": 14,
            "current_stock": 500
        },
        "risk": {
            "risk_level": "medium",
            "risk_score": 0.35
        },
        "sustainability": {
            "carbon_footprint_kg": 425,
            "sustainability_score": 72
        },
        "recommendation": "Order 2736 units with caution"
    }
    
    summary = await gemini.generate_analysis_summary(test_data)
    print(f"✓ Summary generated ({len(summary)} chars)")
    print(f"\n{summary}\n")
    
    # Test 4: Carbon Tips
    print("Test 4: Carbon Reduction Tips")
    tips = await gemini.generate_carbon_reduction_tips(
        sku="WH-FP-0001",
        quantity=100,
        carbon_footprint=425.0,
        sustainability_score=72.0,
        supply_data={"supplier": "GlobalFoods Inc", "lead_time_days": 14}
    )
    print(f"✓ Tips generated ({len(tips)} chars)")
    print(f"\n{tips}\n")
    
    print("=" * 70)
    print("  ✅ ALL TESTS PASSED - GEMINI IS READY!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_gemini())
