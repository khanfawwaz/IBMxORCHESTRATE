"""
IBM watsonx Orchestrate ADK Configuration
Core configuration for the agentic AI orchestration system
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgentRole(str, Enum):
    """Agent role definitions"""
    SOCIAL_ANALYST = "social_analyst"
    SALES_ANALYST = "sales_analyst"
    SIGNAL_PROCESSOR = "signal_processor"
    FORECASTER = "forecaster"
    SUPPLY_MANAGER = "supply_manager"
    RISK_ANALYST = "risk_analyst"
    SUSTAINABILITY_EXPERT = "sustainability_expert"
    XAI_EXPLAINER = "xai_explainer"
    ORCHESTRATOR = "orchestrator"


class AgentCapability(str, Enum):
    """Agent capability types"""
    DATA_COLLECTION = "data_collection"
    DATA_ANALYSIS = "data_analysis"
    ML_PREDICTION = "ml_prediction"
    DECISION_MAKING = "decision_making"
    EXPLANATION = "explanation"
    OPTIMIZATION = "optimization"


class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    role: AgentRole = Field(..., description="Agent role")
    capabilities: List[AgentCapability] = Field(default_factory=list)
    port: int = Field(..., description="Service port")
    endpoint: str = Field(..., description="API endpoint")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    enabled: bool = Field(default=True, description="Agent enabled status")
    priority: int = Field(default=5, description="Agent priority (1-10)")
    dependencies: List[str] = Field(default_factory=list, description="Dependent agent IDs")
    
    class Config:
        use_enum_values = True


class OrchestratorConfig(BaseModel):
    """Main orchestrator configuration"""
    orchestrator_id: str = "unified-orchestrator"
    version: str = "1.0.0"
    max_concurrent_agents: int = 8
    agent_timeout: int = 30
    enable_caching: bool = True
    enable_monitoring: bool = True
    enable_auto_retry: bool = True
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = Field(default_factory=dict)
    
    # Workflow settings
    default_workflow: str = "complete_analysis"
    enable_parallel_execution: bool = True
    
    # IBM watsonx settings
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    
    class Config:
        use_enum_values = True


# Default agent configurations
DEFAULT_AGENTS = {
    "social_agent": AgentConfig(
        agent_id="social_agent",
        agent_name="Social Trend Analyst",
        role=AgentRole.SOCIAL_ANALYST,
        capabilities=[
            AgentCapability.DATA_COLLECTION,
            AgentCapability.DATA_ANALYSIS
        ],
        port=8001,
        endpoint="/api/v1/collect",
        priority=7
    ),
    "sales_agent": AgentConfig(
        agent_id="sales_agent",
        agent_name="Sales Data Analyst",
        role=AgentRole.SALES_ANALYST,
        capabilities=[
            AgentCapability.DATA_COLLECTION,
            AgentCapability.DATA_ANALYSIS
        ],
        port=8002,
        endpoint="/api/v1/ingest",
        priority=9
    ),
    "signal_agent": AgentConfig(
        agent_id="signal_agent",
        agent_name="Signal Processor",
        role=AgentRole.SIGNAL_PROCESSOR,
        capabilities=[
            AgentCapability.DATA_ANALYSIS,
            AgentCapability.OPTIMIZATION
        ],
        port=8003,
        endpoint="/api/v1/filter",
        priority=6,
        dependencies=["social_agent"]
    ),
    "forecast_agent": AgentConfig(
        agent_id="forecast_agent",
        agent_name="ML Forecaster",
        role=AgentRole.FORECASTER,
        capabilities=[
            AgentCapability.ML_PREDICTION,
            AgentCapability.DATA_ANALYSIS
        ],
        port=8004,
        endpoint="/api/v1/forecast",
        priority=10,
        dependencies=["sales_agent", "signal_agent"]
    ),
    "supply_agent": AgentConfig(
        agent_id="supply_agent",
        agent_name="Supply Chain Manager",
        role=AgentRole.SUPPLY_MANAGER,
        capabilities=[
            AgentCapability.DATA_ANALYSIS,
            AgentCapability.OPTIMIZATION
        ],
        port=8005,
        endpoint="/api/v1/check",
        priority=8,
        dependencies=["forecast_agent"]
    ),
    "risk_agent": AgentConfig(
        agent_id="risk_agent",
        agent_name="Risk Analyst",
        role=AgentRole.RISK_ANALYST,
        capabilities=[
            AgentCapability.DATA_ANALYSIS,
            AgentCapability.DECISION_MAKING
        ],
        port=8006,
        endpoint="/api/v1/analyze",
        priority=8,
        dependencies=["forecast_agent", "supply_agent"]
    ),
    "sustainability_agent": AgentConfig(
        agent_id="sustainability_agent",
        agent_name="Sustainability Expert",
        role=AgentRole.SUSTAINABILITY_EXPERT,
        capabilities=[
            AgentCapability.DATA_ANALYSIS,
            AgentCapability.OPTIMIZATION
        ],
        port=8007,
        endpoint="/api/v1/calculate",
        priority=6,
        dependencies=["supply_agent"]
    ),
    "xai_agent": AgentConfig(
        agent_id="xai_agent",
        agent_name="XAI Explainer",
        role=AgentRole.XAI_EXPLAINER,
        capabilities=[
            AgentCapability.EXPLANATION,
            AgentCapability.ML_PREDICTION
        ],
        port=8008,
        endpoint="/api/v1/explain",
        priority=7,
        dependencies=["forecast_agent", "risk_agent"]
    )
}


def get_orchestrator_config() -> OrchestratorConfig:
    """Get default orchestrator configuration"""
    return OrchestratorConfig(
        agents=DEFAULT_AGENTS
    )


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get configuration for specific agent"""
    return DEFAULT_AGENTS.get(agent_id)


def get_execution_order() -> List[str]:
    """
    Get optimal agent execution order based on dependencies
    Returns list of agent IDs in execution order
    """
    # Topological sort based on dependencies
    order = [
        "sales_agent",      # No dependencies
        "social_agent",     # No dependencies
        "signal_agent",     # Depends on social_agent
        "forecast_agent",   # Depends on sales_agent, signal_agent
        "supply_agent",     # Depends on forecast_agent
        "risk_agent",       # Depends on forecast_agent, supply_agent
        "sustainability_agent",  # Depends on supply_agent
        "xai_agent"         # Depends on forecast_agent, risk_agent
    ]
    return order
