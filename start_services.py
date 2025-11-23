"""
Quick Start Script
Starts all backend services for development
"""

import subprocess
import sys
import time
from pathlib import Path
from loguru import logger
import os

PROJECT_ROOT = Path(__file__).parent


def start_service(name: str, script_path: Path, port: int):
    """Start a service in a new process"""
    logger.info(f"Starting {name} on port {port}...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            env={**os.environ, f"{name.upper().replace(' ', '_')}_PORT": str(port)}
        )
        
        logger.success(f"✓ {name} started (PID: {process.pid})")
        return process
        
    except Exception as e:
        logger.error(f"✗ Failed to start {name}: {str(e)}")
        return None


def main():
    """Start all services"""
    print("=" * 70)
    print("  STARTING WAREHOUSE FORECASTING SYSTEM")
    print("=" * 70 + "\n")
    
    processes = []
    
    # Start Forecast Agent
    forecast_script = PROJECT_ROOT / "backend" / "agents" / "forecast_agent" / "app.py"
    if forecast_script.exists():
        p = start_service("Forecast Agent", forecast_script, 8004)
        if p:
            processes.append(("Forecast Agent", p))
            time.sleep(2)
    
    # Start Supply Agent
    supply_script = PROJECT_ROOT / "backend" / "agents" / "supply_agent" / "app.py"
    if supply_script.exists():
        p = start_service("Supply Agent", supply_script, 8005)
        if p:
            processes.append(("Supply Agent", p))
            time.sleep(2)
    
    # Start Unified Orchestrator
    orchestrator_script = PROJECT_ROOT / "backend" / "orchestrator" / "app.py"
    if orchestrator_script.exists():
        p = start_service("Unified Orchestrator", orchestrator_script, 9000)
        if p:
            processes.append(("Unified Orchestrator", p))
            time.sleep(2)
    
    print("\n" + "=" * 70)
    print("  ALL SERVICES STARTED")
    print("=" * 70 + "\n")
    
    print("🚀 Services running:")
    for name, process in processes:
        print(f"  • {name} (PID: {process.pid})")
    
    print("\n📡 API Endpoints:")
    print("  • Forecast Agent:        http://localhost:8004")
    print("  • Supply Agent:          http://localhost:8005")
    print("  • Unified Orchestrator:  http://localhost:9000")
    print("  • API Documentation:     http://localhost:9000/docs")
    
    print("\n💡 Test the API:")
    print("""
  curl -X POST http://localhost:9000/api/v1/analyze \\
    -H "Content-Type: application/json" \\
    -d '{
      "sku": "WH-FP-0001",
      "location": "New York",
      "forecast_days": 30,
      "quantity": 100
    }'
""")
    
    print("\n⚠️  Press Ctrl+C to stop all services\n")
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
            
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"{name} stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n\nStopping all services...")
        
        for name, process in processes:
            logger.info(f"Stopping {name}...")
            process.terminate()
            process.wait(timeout=5)
        
        logger.success("✓ All services stopped")


if __name__ == "__main__":
    main()
