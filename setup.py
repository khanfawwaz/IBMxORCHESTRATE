"""
Complete Setup Script for Warehouse Forecasting System
Initializes database, generates data, trains models, and verifies setup
"""

import sys
from pathlib import Path
import subprocess
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from loguru import logger


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(cmd: str, cwd: Path = PROJECT_ROOT) -> bool:
    """Run command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.success(f"✓ {cmd}")
            return True
        else:
            logger.error(f"✗ {cmd}")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"✗ {cmd}: {str(e)}")
        return False


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    logger.info(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        logger.error("Python 3.10+ required")
        return False
    
    logger.success("✓ Python version OK")
    return True


def create_env_file():
    """Create .env file from template"""
    print_header("Creating Environment File")
    
    env_example = PROJECT_ROOT / ".env.example"
    env_file = PROJECT_ROOT / ".env"
    
    if env_file.exists():
        logger.info(".env file already exists")
        return True
    
    if not env_example.exists():
        logger.error(".env.example not found")
        return False
    
    # Copy template
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    logger.success("✓ Created .env file")
    logger.info("Please update .env with your API keys if needed")
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    logger.info("This may take a few minutes...")
    
    # Upgrade pip
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Install requirements
    requirements_file = PROJECT_ROOT / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error("requirements.txt not found")
        return False
    
    success = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    
    if success:
        logger.success("✓ Dependencies installed")
    
    return success


def generate_warehouse_data():
    """Generate synthetic warehouse data"""
    print_header("Generating Synthetic Warehouse Data")
    
    script_path = PROJECT_ROOT / "ml" / "training" / "generate_warehouse_data.py"
    
    if not script_path.exists():
        logger.error("Data generation script not found")
        return False
    
    logger.info("Generating 500 products and 2.9M sales records...")
    logger.info("This will take 2-5 minutes...")
    
    success = run_command(f"{sys.executable} {script_path}")
    
    if success:
        logger.success("✓ Warehouse data generated")
    
    return success


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
    
    script_path = PROJECT_ROOT / "ml" / "training" / "train_forecast_model.py"
    
    if not script_path.exists():
        logger.error("Model training script not found")
        return False
    
    logger.info("Training Prophet models...")
    logger.info("This will take 3-5 minutes...")
    
    success = run_command(f"{sys.executable} {script_path}")
    
    if success:
        logger.success("✓ ML models trained")
    
    return success


def verify_setup():
    """Verify setup is complete"""
    print_header("Verifying Setup")
    
    checks = []
    
    # Check data files
    data_dir = PROJECT_ROOT / "data" / "warehouse"
    required_files = ["products.csv", "sales_history.csv", "supply_chain.csv"]
    
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            logger.success(f"✓ {filename} exists")
            checks.append(True)
        else:
            logger.error(f"✗ {filename} missing")
            checks.append(False)
    
    # Check database
    db_path = PROJECT_ROOT / "data" / "databases" / "warehouse.db"
    if db_path.exists():
        logger.success(f"✓ Database exists ({db_path.stat().st_size / 1024 / 1024:.1f} MB)")
        checks.append(True)
    else:
        logger.error("✗ Database missing")
        checks.append(False)
    
    # Check models
    model_dir = PROJECT_ROOT / "ml" / "models"
    if model_dir.exists():
        model_files = list(model_dir.glob("*.pkl"))
        if model_files:
            logger.success(f"✓ {len(model_files)} ML models trained")
            checks.append(True)
        else:
            logger.error("✗ No ML models found")
            checks.append(False)
    else:
        logger.error("✗ Model directory missing")
        checks.append(False)
    
    return all(checks)


def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("""
🎉 Your Agentic AI Warehouse Forecasting System is ready!

NEXT STEPS:

1. Start the backend services:
   
   # Start Forecast Agent (Port 8004)
   python backend/agents/forecast_agent/app.py
   
   # Start Supply Agent (Port 8005)
   python backend/agents/supply_agent/app.py
   
   # Start Unified Orchestrator (Port 9000)
   python backend/orchestrator/app.py

2. Test the API:
   
   Open http://localhost:9000/docs in your browser
   
   Or use curl:
   curl -X POST http://localhost:9000/api/v1/analyze \\
     -H "Content-Type: application/json" \\
     -d '{
       "sku": "WH-FP-0001",
       "location": "New York",
       "forecast_days": 30,
       "quantity": 100
     }'

3. Build the frontend:
   
   cd frontend
   npm install
   npm run dev
   
   Then open http://localhost:5173

4. Optional: Set up API keys in .env file
   - SERPAPI_KEY for Google Trends
   - GEMINI_API_KEY for AI summaries

📚 Documentation: See README.md for more details
🐛 Issues: Check logs/ directory for debugging

Happy forecasting! 🚀
""")


def main():
    """Main setup function"""
    print_header("Agentic AI Warehouse Forecasting System - Setup")
    
    logger.info("Starting automated setup...")
    
    # Step 1: Check Python version
    if not check_python_version():
        logger.error("Setup failed: Python version check")
        return False
    
    # Step 2: Create .env file
    if not create_env_file():
        logger.error("Setup failed: Environment file creation")
        return False
    
    # Step 3: Install dependencies
    if not install_dependencies():
        logger.error("Setup failed: Dependency installation")
        logger.info("You may need to install dependencies manually:")
        logger.info(f"  {sys.executable} -m pip install -r requirements.txt")
        return False
    
    # Step 4: Generate data
    if not generate_warehouse_data():
        logger.error("Setup failed: Data generation")
        return False
    
    # Step 5: Initialize database
    if not initialize_database():
        logger.error("Setup failed: Database initialization")
        return False
    
    # Step 6: Train models
    if not train_ml_models():
        logger.error("Setup failed: Model training")
        return False
    
    # Step 7: Verify setup
    if not verify_setup():
        logger.error("Setup verification failed")
        return False
    
    # Print next steps
    print_next_steps()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
