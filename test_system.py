"""
Comprehensive System Test
Tests all components of the warehouse forecasting system
"""

import sys
from pathlib import Path
import asyncio
import json

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from loguru import logger
import httpx


class SystemTester:
    """System testing class"""
    
    def __init__(self):
        self.base_url = "http://localhost"
        self.timeout = 30.0
        self.results = []
    
    async def test_forecast_agent(self):
        """Test forecast agent"""
        logger.info("Testing Forecast Agent...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Health check
                response = await client.get(f"{self.base_url}:8004/")
                assert response.status_code == 200
                logger.success("✓ Forecast Agent health check passed")
                
                # Forecast request
                response = await client.post(
                    f"{self.base_url}:8004/api/v1/forecast",
                    json={
                        "sku": "WH-FP-0001",
                        "location": "New York",
                        "forecast_days": 30
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "total_predicted_demand" in data
                assert "trend" in data
                assert "confidence" in data
                
                logger.success(f"✓ Forecast Agent test passed")
                logger.info(f"  Predicted demand: {data['total_predicted_demand']:.0f} units")
                logger.info(f"  Trend: {data['trend']}")
                logger.info(f"  Confidence: {data['confidence']:.0%}")
                
                self.results.append(("Forecast Agent", True, data))
                return True
                
        except Exception as e:
            logger.error(f"✗ Forecast Agent test failed: {str(e)}")
            self.results.append(("Forecast Agent", False, str(e)))
            return False
    
    async def test_supply_agent(self):
        """Test supply agent"""
        logger.info("Testing Supply Agent...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Health check
                response = await client.get(f"{self.base_url}:8005/")
                assert response.status_code == 200
                logger.success("✓ Supply Agent health check passed")
                
                # Supply check request
                response = await client.post(
                    f"{self.base_url}:8005/api/v1/check",
                    json={
                        "sku": "WH-FP-0001",
                        "quantity": 100,
                        "location": "New York"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "supplier" in data
                assert "lead_time_days" in data
                assert "feasibility" in data
                
                logger.success(f"✓ Supply Agent test passed")
                logger.info(f"  Supplier: {data['supplier']}")
                logger.info(f"  Lead time: {data['lead_time_days']} days")
                logger.info(f"  Feasibility: {data['feasibility']}")
                
                self.results.append(("Supply Agent", True, data))
                return True
                
        except Exception as e:
            logger.error(f"✗ Supply Agent test failed: {str(e)}")
            self.results.append(("Supply Agent", False, str(e)))
            return False
    
    async def test_unified_orchestrator(self):
        """Test unified orchestrator"""
        logger.info("Testing Unified Orchestrator...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Health check
                response = await client.get(f"{self.base_url}:9000/")
                assert response.status_code == 200
                logger.success("✓ Unified Orchestrator health check passed")
                
                # Complete analysis request
                response = await client.post(
                    f"{self.base_url}:9000/api/v1/analyze",
                    json={
                        "sku": "WH-FP-0001",
                        "location": "New York",
                        "forecast_days": 30,
                        "quantity": 100,
                        "knowledge_context": "Product trending on social media"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify all components
                assert "forecast" in data
                assert "supply" in data
                assert "risk" in data
                assert "sustainability" in data
                assert "explanation" in data
                assert "recommendation" in data
                assert "overall_confidence" in data
                
                logger.success(f"✓ Unified Orchestrator test passed")
                logger.info(f"  Recommendation: {data['recommendation']}")
                logger.info(f"  Overall confidence: {data['overall_confidence']:.0%}")
                logger.info(f"  Risk level: {data['risk']['risk_level']}")
                logger.info(f"  Sustainability score: {data['sustainability']['sustainability_score']:.0f}/100")
                
                self.results.append(("Unified Orchestrator", True, data))
                return True
                
        except Exception as e:
            logger.error(f"✗ Unified Orchestrator test failed: {str(e)}")
            self.results.append(("Unified Orchestrator", False, str(e)))
            return False
    
    async def test_database(self):
        """Test database connectivity"""
        logger.info("Testing Database...")
        
        try:
            from backend.shared.database import get_db, Product, SalesHistory
            
            with get_db() as db:
                # Check products
                product_count = db.query(Product).count()
                assert product_count > 0
                logger.success(f"✓ Database has {product_count} products")
                
                # Check sales history
                sales_count = db.query(SalesHistory).count()
                assert sales_count > 0
                logger.success(f"✓ Database has {sales_count:,} sales records")
                
                self.results.append(("Database", True, {
                    "products": product_count,
                    "sales": sales_count
                }))
                return True
                
        except Exception as e:
            logger.error(f"✗ Database test failed: {str(e)}")
            self.results.append(("Database", False, str(e)))
            return False
    
    async def test_ml_models(self):
        """Test ML models"""
        logger.info("Testing ML Models...")
        
        try:
            model_dir = PROJECT_ROOT / "ml" / "models"
            
            if not model_dir.exists():
                raise Exception("Model directory not found")
            
            model_files = list(model_dir.glob("*.pkl"))
            
            if len(model_files) == 0:
                raise Exception("No trained models found")
            
            logger.success(f"✓ Found {len(model_files)} trained models")
            
            # Try to load a model
            import joblib
            baseline_model = model_dir / "prophet_baseline.pkl"
            
            if baseline_model.exists():
                model = joblib.load(baseline_model)
                logger.success("✓ Successfully loaded baseline model")
            
            self.results.append(("ML Models", True, {
                "model_count": len(model_files)
            }))
            return True
            
        except Exception as e:
            logger.error(f"✗ ML Models test failed: {str(e)}")
            self.results.append(("ML Models", False, str(e)))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70 + "\n")
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        for component, success, data in self.results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status:10} {component}")
        
        print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("\n🎉 All tests passed! System is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the logs above.")


async def main():
    """Run all tests"""
    print("=" * 70)
    print("  WAREHOUSE FORECASTING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 70 + "\n")
    
    tester = SystemTester()
    
    # Test database and models first (don't require services)
    await tester.test_database()
    await tester.test_ml_models()
    
    # Test services (require services to be running)
    logger.info("\nTesting services (make sure they are running)...")
    await tester.test_forecast_agent()
    await tester.test_supply_agent()
    await tester.test_unified_orchestrator()
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
