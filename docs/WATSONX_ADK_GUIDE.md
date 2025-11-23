# IBM watsonx Orchestrate ADK Integration Guide

## Overview

This system is built with **IBM watsonx Orchestrate ADK** at its core, providing enterprise-grade agentic AI capabilities for autonomous inventory management and forecasting.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│         IBM watsonx Orchestrate ADK (Core Engine)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Agent Registry│  │Workflow Engine│  │Message Broker│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Social Agent │   │Forecast Agent│   │ Supply Agent │
│  (Port 8001) │   │  (Port 8004) │   │  (Port 8005) │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Key Features

### 1. Agent Orchestration

The ADK coordinates multiple specialized agents:

**File:** `adk/workflows/orchestration_engine.py`

```python
from adk.workflows.orchestration_engine import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator(config)

# Register agents
orchestrator.register_agent(forecast_agent)
orchestrator.register_agent(supply_agent)

# Execute workflow
result = await orchestrator.execute_workflow(
    workflow_id="complete_analysis",
    context={"sku": "WH-FP-0001", "location": "New York"}
)
```

### 2. Workflow Definition

**File:** `adk/workflows/orchestration_engine.py`

```python
workflow = Workflow(
    workflow_id="complete_analysis",
    workflow_name="Complete Inventory Analysis",
    parallel_execution=True,
    steps=[
        WorkflowStep(
            step_id="collect_sales",
            agent_id="sales_agent",
            action="ingest",
            depends_on=[]
        ),
        WorkflowStep(
            step_id="generate_forecast",
            agent_id="forecast_agent",
            action="forecast",
            depends_on=["collect_sales"]
        ),
        # ... more steps
    ]
)
```

### 3. Agent Base Class

**File:** `adk/agents/base_agent.py`

All agents inherit from `BaseAgent`:

```python
class ForecastAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="forecast_agent",
            agent_name="ML Forecaster",
            capabilities=["ml_prediction", "data_analysis"]
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        # Agent-specific logic
        forecast = await self.generate_forecast(...)
        
        return AgentResult(
            agent_id=self.agent_id,
            task_id=task.task_id,
            status=AgentStatus.SUCCESS,
            result=forecast.dict(),
            confidence=forecast.confidence
        )
```

### 4. Inter-Agent Communication

Agents communicate via message passing:

```python
# Agent A sends message to Agent B
message = AgentMessage(
    message_id="msg_001",
    sender_id="forecast_agent",
    receiver_id="supply_agent",
    message_type="forecast_complete",
    payload={"predicted_demand": 3420}
)

await orchestrator.broadcast_message(
    sender_id="forecast_agent",
    message_type="forecast_complete",
    payload=forecast_data
)
```

## Configuration

### Agent Configuration

**File:** `adk/config/orchestrator_config.py`

```python
agent_config = AgentConfig(
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
)
```

### Orchestrator Configuration

```python
orchestrator_config = OrchestratorConfig(
    orchestrator_id="unified-orchestrator",
    version="1.0.0",
    max_concurrent_agents=8,
    agent_timeout=30,
    enable_caching=True,
    enable_monitoring=True,
    agents={
        "forecast_agent": forecast_config,
        "supply_agent": supply_config,
        # ... more agents
    }
)
```

## Workflow Execution

### Sequential Execution

```python
# Execute steps one by one
result = await orchestrator.execute_workflow(
    workflow_id="complete_analysis",
    context=request_context
)
```

### Parallel Execution

```python
# Execute independent steps in parallel
workflow = Workflow(
    workflow_id="parallel_analysis",
    parallel_execution=True,  # Enable parallel execution
    steps=[
        # Steps without dependencies run in parallel
        WorkflowStep(step_id="collect_social", depends_on=[]),
        WorkflowStep(step_id="collect_sales", depends_on=[]),
        # This waits for both above
        WorkflowStep(step_id="analyze", depends_on=["collect_social", "collect_sales"])
    ]
)
```

### Dependency Resolution

The orchestrator automatically resolves dependencies:

```python
# Dependency graph
collect_sales → generate_forecast → check_supply → analyze_risk
                                  ↘ calculate_sustainability
```

## Agent Capabilities

### 1. Autonomous Decision Making

Agents make decisions based on their analysis:

```python
class RiskAgent(BaseAgent):
    async def execute(self, task: AgentTask) -> AgentResult:
        # Analyze risk factors
        risk_score = self.calculate_risk(...)
        
        # Make autonomous decision
        if risk_score > 0.8:
            recommendation = "HOLD - Critical risk detected"
        elif risk_score > 0.6:
            recommendation = "CAUTION - High risk"
        else:
            recommendation = "PROCEED - Low risk"
        
        return AgentResult(
            result={"recommendation": recommendation},
            confidence=self.calculate_confidence(risk_score)
        )
```

### 2. Adaptive Learning

Agents learn from feedback:

```python
async def learn_from_feedback(self, task_id: str, feedback: Dict):
    # Store feedback
    self.memory.store_long_term(f"feedback_{task_id}", feedback)
    
    # Adjust future predictions
    if feedback["actual_demand"] > feedback["predicted_demand"]:
        self.adjustment_factor *= 1.1  # Increase future predictions
```

### 3. Agent Memory

Agents maintain short-term and long-term memory:

```python
class AgentMemory:
    def __init__(self):
        self.short_term: List[Dict] = []  # Recent interactions
        self.long_term: Dict[str, Any] = {}  # Learned patterns
    
    def store_short_term(self, data: Dict):
        self.short_term.append(data)
        if len(self.short_term) > 1000:
            self.short_term.pop(0)
    
    def retrieve(self, key: str) -> Any:
        return self.long_term.get(key)
```

## Error Handling & Resilience

### Retry Logic

```python
# Automatic retry with exponential backoff
step = WorkflowStep(
    step_id="generate_forecast",
    agent_id="forecast_agent",
    retry_on_failure=True,
    max_retries=3
)
```

### Fallback Strategies

```python
async def execute_with_fallback(self, task: AgentTask):
    try:
        # Try primary method
        return await self.execute_primary(task)
    except Exception as e:
        logger.warning(f"Primary method failed: {e}")
        # Use fallback
        return await self.execute_fallback(task)
```

### Optional Steps

```python
# Step can fail without breaking workflow
WorkflowStep(
    step_id="collect_social",
    agent_id="social_agent",
    optional=True  # Workflow continues even if this fails
)
```

## Monitoring & Observability

### Agent Status

```python
# Get status of all agents
status = orchestrator.get_all_agent_status()

# Output:
{
    "forecast_agent": {
        "status": "idle",
        "tasks_completed": 42,
        "success_rate": 0.95,
        "average_execution_time": 1.2
    },
    ...
}
```

### Execution History

```python
# Get recent workflow executions
history = orchestrator.get_execution_history(limit=10)

for execution in history:
    print(f"Workflow: {execution.workflow_id}")
    print(f"Status: {execution.status}")
    print(f"Confidence: {execution.overall_confidence}")
    print(f"Time: {execution.execution_time}s")
```

## Integration with IBM watsonx

### 1. Export Workflow Definition

```python
# Export workflow for watsonx Orchestrate
workflow_yaml = workflow.to_yaml()

# Save to file
with open("orchestrate/workflows/complete_analysis.yaml", "w") as f:
    f.write(workflow_yaml)
```

### 2. OpenAPI Specification

Each agent exposes an OpenAPI spec:

```yaml
# orchestrate/tools/forecast-agent.yaml
openapi: 3.0.0
info:
  title: Forecast Agent
  version: 1.0.0

paths:
  /api/v1/forecast:
    post:
      operationId: generateForecast
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ForecastRequest'
```

### 3. Agent Registration

```yaml
# orchestrate/agents/forecast-agent.yaml
name: forecast-agent
description: ML-powered demand forecasting
triggers:
  - schedule: "0 9 * * *"  # Daily at 9 AM
  - event: "new_product_request"

skills:
  - id: generate_forecast
    endpoint: http://localhost:8004/api/v1/forecast
    method: POST
```

## Best Practices

### 1. Agent Design

- ✅ Single responsibility per agent
- ✅ Clear input/output contracts
- ✅ Idempotent operations
- ✅ Graceful degradation

### 2. Workflow Design

- ✅ Minimize dependencies for parallelism
- ✅ Use optional steps for non-critical tasks
- ✅ Set appropriate timeouts
- ✅ Implement retry logic

### 3. Error Handling

- ✅ Always provide fallback strategies
- ✅ Log all errors with context
- ✅ Return partial results when possible
- ✅ Use circuit breakers for external services

### 4. Performance

- ✅ Cache frequently accessed data
- ✅ Use async/await for I/O operations
- ✅ Implement connection pooling
- ✅ Monitor and optimize slow agents

## Example: Complete Analysis Workflow

```python
# 1. Define workflow
workflow = create_complete_analysis_workflow()

# 2. Register with orchestrator
orchestrator.register_workflow(workflow)

# 3. Execute
result = await orchestrator.execute_workflow(
    workflow_id="complete_analysis",
    context={
        "sku": "WH-FP-0001",
        "location": "New York",
        "forecast_days": 30,
        "quantity": 100
    }
)

# 4. Process results
if result.status == "success":
    forecast = result.agent_results["forecast_agent"]
    supply = result.agent_results["supply_agent"]
    risk = result.agent_results["risk_agent"]
    
    print(f"Recommendation: {generate_recommendation(forecast, supply, risk)}")
    print(f"Confidence: {result.overall_confidence:.0%}")
```

## Deployment

### Local Development

```bash
python start_services.py
```

### Docker

```bash
docker-compose up -d
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-orchestrator
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: orchestrator
        image: warehouse-orchestrator:latest
        env:
        - name: WATSONX_API_KEY
          valueFrom:
            secretKeyRef:
              name: watsonx-credentials
              key: api-key
```

## Conclusion

The IBM watsonx Orchestrate ADK provides a robust foundation for building agentic AI systems with:

- 🤖 **Autonomous Agents** - Self-directed decision making
- 🔄 **Workflow Orchestration** - Complex multi-step processes
- 📡 **Inter-Agent Communication** - Coordinated collaboration
- 🛡️ **Resilience** - Error handling and retry logic
- 📊 **Observability** - Monitoring and debugging
- 🚀 **Scalability** - Horizontal scaling support

For more information, see:
- [IBM watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/orchestrate)
- [Agent Development Guide](docs/agent-development.md)
- [Workflow Design Patterns](docs/workflow-patterns.md)
