"""
Quick Setup - Generate Data and Train Models Only
Skips dependency installation (assumes already installed)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from loguru import logger


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def generate_warehouse_data():
    """Generate synthetic warehouse data"""
    print_header("Generating Synthetic Warehouse Data")
    
    try:
        # Import and run data generator
        import ml.training.generate_warehouse_data as gen
        gen.generate_all_data()
        return True
    except Exception as e:
        logger.error(f"Data generation failed: {str(e)}")
        return False


def initialize_database():
    """Initialize and seed database"""
    print_header("Initializing Database")
    
    try:
        from backend.shared.database import init_database, seed_database
        
        logger.info("Creating database tables...")
        init_database()
        
        logger.info("Seeding database with generated data...")
        seed_database()
        
        logger.success("✓ Database initialized and seeded")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


def train_ml_models():
    """Train ML forecasting models"""
    print_header("Training ML Models")
    
    try:
        # Import and run model training
        import ml.training.train_forecast_model as trainer
        trainer.main()
        return True
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        return False


def main():
    """Main quick setup function"""
    print_header("Quick Setup - Data & Models")
    
    logger.info("Starting quick setup (skipping dependency install)...")
    
    # Step 1: Generate data
    if not generate_warehouse_data():
        logger.error("Setup failed: Data generation")
        return False
    
    # Step 2: Initialize database
    if not initialize_database():
        logger.error("Setup failed: Database initialization")
        return False
    
    # Step 3: Train models
    if not train_ml_models():
        logger.error("Setup failed: Model training")
        return False
    
    print_header("Setup Complete!")
    
    print("""
🎉 Data and models are ready!

NEXT STEPS:

1. Start the services:
   python start_services.py

2. Test the system:
   python test_system.py

3. Try the API:
   http://localhost:9000/docs

Happy forecasting! 🚀
""")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
