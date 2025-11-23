"""
IBM watsonx Orchestrate ADK - Core Orchestration Engine
Coordinates multiple AI agents to achieve complex goals
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import asyncio
from loguru import logger
from pydantic import BaseModel, Field

from adk.agents.base_agent import (
    BaseAgent, AgentTask, AgentResult, AgentStatus, AgentMessage
)
from adk.config.orchestrator_config import (
    OrchestratorConfig, AgentConfig, get_execution_order
)


class WorkflowStep(BaseModel):
    """Single step in a workflow"""
    step_id: str
    agent_id: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    optional: bool = False
    retry_on_failure: bool = True
    max_retries: int = 3


class Workflow(BaseModel):
    """Workflow definition"""
    workflow_id: str
    workflow_name: str
    description: str
    steps: List[WorkflowStep]
    parallel_execution: bool = True
    timeout: int = 300  # seconds


class OrchestrationResult(BaseModel):
    """Result from workflow orchestration"""
    workflow_id: str
    status: str
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)
    execution_time: float
    overall_confidence: float
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentOrchestrator:
    """
    Core orchestration engine for coordinating multiple AI agents
    Implements IBM watsonx Orchestrate ADK patterns
    """
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[OrchestrationResult] = []
        
        logger.info(
            f"Initialized orchestrator with {len(config.agents)} agents"
        )
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator
        
        Args:
            agent: Agent instance to register
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_name}")
    
    def register_workflow(self, workflow: Workflow) -> None:
        """
        Register a workflow
        
        Args:
            workflow: Workflow definition
        """
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow.workflow_name}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> OrchestrationResult:
        """
        Execute a registered workflow
        
        Args:
            workflow_id: ID of workflow to execute
            context: Shared context for all agents
            
        Returns:
            OrchestrationResult with outcomes from all agents
        """
        start_time = datetime.now()
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        logger.info(f"Executing workflow: {workflow.workflow_name}")
        
        agent_results: Dict[str, AgentResult] = {}
        errors: List[str] = []
        
        try:
            if workflow.parallel_execution:
                # Execute independent steps in parallel
                agent_results = await self._execute_parallel(
                    workflow, context
                )
            else:
                # Execute steps sequentially
                agent_results = await self._execute_sequential(
                    workflow, context
                )
            
            # Calculate overall confidence
            confidences = [
                r.confidence for r in agent_results.values()
                if r.status == AgentStatus.SUCCESS
            ]
            overall_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )
            
            # Collect errors
            errors = [
                f"{r.agent_id}: {r.error}"
                for r in agent_results.values()
                if r.error
            ]
            
            status = "success" if not errors else "partial_success"
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            status = "failed"
            overall_confidence = 0.0
            errors.append(str(e))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result = OrchestrationResult(
            workflow_id=workflow_id,
            status=status,
            agent_results=agent_results,
            execution_time=execution_time,
            overall_confidence=overall_confidence,
            errors=errors
        )
        
        self.execution_history.append(result)
        
        logger.info(
            f"Workflow completed in {execution_time:.2f}s "
            f"with confidence {overall_confidence:.2f}"
        )
        
        return result
    
    async def _execute_parallel(
        self,
        workflow: Workflow,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """
        Execute workflow steps in parallel where possible
        
        Args:
            workflow: Workflow to execute
            context: Shared context
            
        Returns:
            Dictionary of agent results
        """
        results: Dict[str, AgentResult] = {}
        completed_steps: set = set()
        
        # Build dependency graph
        dependency_graph = {
            step.step_id: step.depends_on
            for step in workflow.steps
        }
        
        while len(completed_steps) < len(workflow.steps):
            # Find steps ready to execute
            ready_steps = [
                step for step in workflow.steps
                if step.step_id not in completed_steps
                and all(dep in completed_steps for dep in step.depends_on)
            ]
            
            if not ready_steps:
                break
            
            # Execute ready steps in parallel
            tasks = [
                self._execute_step(step, context, results)
                for step in ready_steps
            ]
            
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for step, result in zip(ready_steps, step_results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Step {step.step_id} failed: {str(result)}"
                    )
                    if not step.optional:
                        raise result
                else:
                    results[step.agent_id] = result
                    completed_steps.add(step.step_id)
        
        return results
    
    async def _execute_sequential(
        self,
        workflow: Workflow,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """
        Execute workflow steps sequentially
        
        Args:
            workflow: Workflow to execute
            context: Shared context
            
        Returns:
            Dictionary of agent results
        """
        results: Dict[str, AgentResult] = {}
        
        for step in workflow.steps:
            result = await self._execute_step(step, context, results)
            results[step.agent_id] = result
            
            if result.status == AgentStatus.FAILED and not step.optional:
                raise RuntimeError(
                    f"Required step {step.step_id} failed: {result.error}"
                )
        
        return results
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        previous_results: Dict[str, AgentResult]
    ) -> AgentResult:
        """
        Execute a single workflow step
        
        Args:
            step: Step to execute
            context: Shared context
            previous_results: Results from previous steps
            
        Returns:
            AgentResult from step execution
        """
        agent = self.agents.get(step.agent_id)
        if not agent:
            raise ValueError(f"Agent {step.agent_id} not found")
        
        # Build task with context from previous steps
        task_context = {**context}
        for dep_step_id in step.depends_on:
            # Find the agent result for this dependency
            for agent_id, result in previous_results.items():
                if result.task_id == dep_step_id:
                    task_context[f"{agent_id}_result"] = result.result
        
        task = AgentTask(
            task_id=step.step_id,
            task_type=step.action,
            parameters=step.parameters,
            context=task_context
        )
        
        # Execute with retry logic
        retries = 0
        while retries <= step.max_retries:
            result = await agent.process_task(task)
            
            if result.status == AgentStatus.SUCCESS:
                return result
            
            if not step.retry_on_failure:
                return result
            
            retries += 1
            if retries <= step.max_retries:
                logger.warning(
                    f"Retrying step {step.step_id} "
                    f"(attempt {retries}/{step.max_retries})"
                )
                await asyncio.sleep(2 ** retries)  # Exponential backoff
        
        return result
    
    async def coordinate_agents(
        self,
        agent_ids: List[str],
        shared_goal: str,
        context: Dict[str, Any]
    ) -> Dict[str, AgentResult]:
        """
        Coordinate multiple agents to achieve a shared goal
        
        Args:
            agent_ids: List of agent IDs to coordinate
            shared_goal: Description of the shared goal
            context: Shared context
            
        Returns:
            Dictionary of agent results
        """
        logger.info(f"Coordinating {len(agent_ids)} agents for goal: {shared_goal}")
        
        # Create tasks for each agent
        tasks = []
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not found, skipping")
                continue
            
            task = AgentTask(
                task_id=f"{agent_id}_{datetime.now().timestamp()}",
                task_type="coordinate",
                parameters={"goal": shared_goal},
                context=context
            )
            
            tasks.append(agent.process_task(task))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        agent_results = {}
        for agent_id, result in zip(agent_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_id} failed: {str(result)}")
            else:
                agent_results[agent_id] = result
        
        return agent_results
    
    async def broadcast_message(
        self,
        sender_id: str,
        message_type: str,
        payload: Dict[str, Any],
        target_agents: Optional[List[str]] = None
    ) -> None:
        """
        Broadcast message to agents
        
        Args:
            sender_id: Sending agent ID
            message_type: Type of message
            payload: Message payload
            target_agents: List of target agent IDs (None = all agents)
        """
        targets = target_agents or list(self.agents.keys())
        
        for target_id in targets:
            if target_id == sender_id:
                continue
            
            agent = self.agents.get(target_id)
            if not agent:
                continue
            
            message = AgentMessage(
                message_id=f"{sender_id}_{target_id}_{datetime.now().timestamp()}",
                sender_id=sender_id,
                receiver_id=target_id,
                message_type=message_type,
                payload=payload
            )
            
            await agent.send_message(message)
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific agent"""
        agent = self.agents.get(agent_id)
        return agent.get_status() if agent else None
    
    def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    def get_execution_history(
        self,
        limit: int = 10
    ) -> List[OrchestrationResult]:
        """Get recent execution history"""
        return self.execution_history[-limit:]


# Predefined workflows
def create_complete_analysis_workflow() -> Workflow:
    """Create the complete analysis workflow"""
    return Workflow(
        workflow_id="complete_analysis",
        workflow_name="Complete Inventory Analysis",
        description="Full analysis including forecasting, risk, and sustainability",
        parallel_execution=True,
        steps=[
            WorkflowStep(
                step_id="collect_sales",
                agent_id="sales_agent",
                action="ingest",
                depends_on=[]
            ),
            WorkflowStep(
                step_id="collect_social",
                agent_id="social_agent",
                action="collect",
                depends_on=[]
            ),
            WorkflowStep(
                step_id="filter_signals",
                agent_id="signal_agent",
                action="filter",
                depends_on=["collect_social"]
            ),
            WorkflowStep(
                step_id="generate_forecast",
                agent_id="forecast_agent",
                action="forecast",
                depends_on=["collect_sales", "filter_signals"]
            ),
            WorkflowStep(
                step_id="check_supply",
                agent_id="supply_agent",
                action="check",
                depends_on=["generate_forecast"]
            ),
            WorkflowStep(
                step_id="analyze_risk",
                agent_id="risk_agent",
                action="analyze",
                depends_on=["generate_forecast", "check_supply"]
            ),
            WorkflowStep(
                step_id="calculate_sustainability",
                agent_id="sustainability_agent",
                action="calculate",
                depends_on=["check_supply"]
            ),
            WorkflowStep(
                step_id="explain_decision",
                agent_id="xai_agent",
                action="explain",
                depends_on=["generate_forecast", "analyze_risk"]
            )
        ]
    )
