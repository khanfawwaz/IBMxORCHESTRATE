"""
Supply Chain Agent - Supplier Availability & Lead Time Management
Port 8005
Checks supplier availability, stock levels, and calculates feasibility
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.shared.models import (
    SupplyCheckRequest, SupplyCheckResponse, SupplyFeasibility,
    HealthCheckResponse
)
from backend.shared.database import get_db, get_supply_chain_info
from adk.agents.base_agent import BaseAgent, AgentTask, AgentResult, AgentStatus

from loguru import logger
import os

app = FastAPI(
    title="Supply Chain Agent",
    description="Supply chain availability and lead time management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SupplyAgentImpl(BaseAgent):
    """Supply Chain Agent Implementation"""
    
    def __init__(self):
        super().__init__(
            agent_id="supply_agent",
            agent_name="Supply Chain Manager",
            capabilities=["data_analysis", "optimization"]
        )
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate supply check request"""
        params = task.parameters
        return all(key in params for key in ["sku", "quantity", "location"])
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute supply chain check"""
        params = task.parameters
        
        supply_response = await self.check_supply(
            sku=params["sku"],
            quantity=params["quantity"],
            location=params["location"]
        )
        
        return AgentResult(
            agent_id=self.agent_id,
            task_id=task.task_id,
            status=AgentStatus.SUCCESS,
            result=supply_response.dict(),
            confidence=0.9,
            metadata={"supplier": supply_response.supplier}
        )
    
    async def check_supply(
        self,
        sku: str,
        quantity: int,
        location: str
    ) -> SupplyCheckResponse:
        """
        Check supply chain availability
        
        Args:
            sku: Product SKU
            quantity: Required quantity
            location: Delivery location
            
        Returns:
            SupplyCheckResponse with availability info
        """
        logger.info(f"Checking supply for {quantity} units of {sku} to {location}")
        
        # Get supply chain data from database
        with get_db() as db:
            supply_info = get_supply_chain_info(db, sku)
        
        if not supply_info:
            # No supply chain data available
            logger.warning(f"No supply chain data for {sku}")
            return SupplyCheckResponse(
                sku=sku,
                supplier="Unknown",
                lead_time_days=30,
                current_stock=0,
                availability="unknown",
                feasibility=SupplyFeasibility.DELAYED,
                unit_cost=0.0,
                minimum_order_quantity=1
            )
        
        # Determine availability
        if supply_info.current_stock >= quantity:
            availability = "in_stock"
        elif supply_info.current_stock >= quantity * 0.5:
            availability = "partial_stock"
        else:
            availability = "out_of_stock"
        
        # Determine feasibility based on lead time
        lead_time = supply_info.lead_time_days
        
        if availability == "in_stock" and lead_time <= 3:
            feasibility = SupplyFeasibility.IMMEDIATE
        elif lead_time <= 7:
            feasibility = SupplyFeasibility.WITHIN_WEEK
        elif lead_time <= 30:
            feasibility = SupplyFeasibility.WITHIN_MONTH
        elif lead_time <= 60:
            feasibility = SupplyFeasibility.DELAYED
        else:
            feasibility = SupplyFeasibility.UNAVAILABLE
        
        return SupplyCheckResponse(
            sku=sku,
            supplier=supply_info.supplier,
            lead_time_days=lead_time,
            current_stock=supply_info.current_stock,
            availability=availability,
            feasibility=feasibility,
            unit_cost=supply_info.unit_cost,
            minimum_order_quantity=supply_info.minimum_order_quantity
        )


supply_agent = SupplyAgentImpl()


@app.get("/", response_model=HealthCheckResponse)
async def root():
    return HealthCheckResponse(
        status="healthy",
        agent_id="supply_agent",
        version="1.0.0"
    )


@app.post("/api/v1/check", response_model=SupplyCheckResponse)
async def check_supply(request: SupplyCheckRequest):
    """Check supply chain availability"""
    try:
        return await supply_agent.check_supply(
            sku=request.sku,
            quantity=request.quantity,
            location=request.location
        )
    except Exception as e:
        logger.error(f"Supply check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("SUPPLY_AGENT_PORT", 8005))
    logger.info(f"Starting Supply Agent on port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
