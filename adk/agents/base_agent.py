"""
Base Agent Class for IBM watsonx Orchestrate ADK
Provides common functionality for all specialized agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import asyncio
import logging
from loguru import logger


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentMessage(BaseModel):
    """Message format for inter-agent communication"""
    message_id: str = Field(..., description="Unique message ID")
    sender_id: str = Field(..., description="Sending agent ID")
    receiver_id: str = Field(..., description="Receiving agent ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: str = Field(..., description="Message type")
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, description="Message priority (1-10)")


class AgentTask(BaseModel):
    """Task definition for agents"""
    task_id: str = Field(..., description="Unique task ID")
    task_type: str = Field(..., description="Task type")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict, description="Shared context")
    created_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    priority: int = Field(default=5)


class AgentResult(BaseModel):
    """Result from agent execution"""
    agent_id: str = Field(..., description="Agent ID")
    task_id: str = Field(..., description="Task ID")
    status: AgentStatus = Field(..., description="Execution status")
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = Field(..., description="Execution time in seconds")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    Base class for all agentic AI agents
    Implements common functionality and enforces agent interface
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.task_history: List[AgentResult] = []
        
        # Setup logging
        self.logger = logger.bind(agent=agent_id)
        self.logger.info(f"Initialized agent: {agent_name}")
    
    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute agent task - must be implemented by subclasses
        
        Args:
            task: Task to execute
            
        Returns:
            AgentResult with execution outcome
        """
        pass
    
    @abstractmethod
    async def validate_input(self, task: AgentTask) -> bool:
        """
        Validate task input - must be implemented by subclasses
        
        Args:
            task: Task to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process task with error handling and monitoring
        
        Args:
            task: Task to process
            
        Returns:
            AgentResult with execution outcome
        """
        start_time = datetime.now()
        self.status = AgentStatus.RUNNING
        
        try:
            # Validate input
            if not await self.validate_input(task):
                raise ValueError(f"Invalid task input for {self.agent_id}")
            
            self.logger.info(f"Processing task {task.task_id}")
            
            # Execute task
            result = await self.execute(task)
            result.execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update status
            self.status = AgentStatus.SUCCESS
            self.task_history.append(result)
            
            self.logger.success(
                f"Task {task.task_id} completed in {result.execution_time:.2f}s"
            )
            
            return result
            
        except asyncio.TimeoutError:
            self.status = AgentStatus.TIMEOUT
            error_result = AgentResult(
                agent_id=self.agent_id,
                task_id=task.task_id,
                status=AgentStatus.TIMEOUT,
                error="Task execution timeout",
                execution_time=(datetime.now() - start_time).total_seconds(),
                confidence=0.0
            )
            self.task_history.append(error_result)
            self.logger.error(f"Task {task.task_id} timeout")
            return error_result
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            error_result = AgentResult(
                agent_id=self.agent_id,
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds(),
                confidence=0.0
            )
            self.task_history.append(error_result)
            self.logger.error(f"Task {task.task_id} failed: {str(e)}")
            return error_result
        
        finally:
            if self.status == AgentStatus.RUNNING:
                self.status = AgentStatus.IDLE
    
    async def send_message(self, message: AgentMessage) -> None:
        """
        Send message to another agent
        
        Args:
            message: Message to send
        """
        self.logger.debug(
            f"Sending message {message.message_id} to {message.receiver_id}"
        )
        # In a real implementation, this would use a message broker
        # For now, we'll use direct queue communication
        await self.message_queue.put(message)
    
    async def receive_message(self, timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """
        Receive message from queue
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            AgentMessage or None if timeout
        """
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=timeout
                )
            else:
                message = await self.message_queue.get()
            
            self.logger.debug(f"Received message {message.message_id}")
            return message
            
        except asyncio.TimeoutError:
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "tasks_completed": len(self.task_history),
            "success_rate": self._calculate_success_rate(),
            "average_execution_time": self._calculate_avg_execution_time()
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate task success rate"""
        if not self.task_history:
            return 0.0
        
        successful = sum(
            1 for result in self.task_history
            if result.status == AgentStatus.SUCCESS
        )
        return successful / len(self.task_history)
    
    def _calculate_avg_execution_time(self) -> float:
        """Calculate average execution time"""
        if not self.task_history:
            return 0.0
        
        total_time = sum(result.execution_time for result in self.task_history)
        return total_time / len(self.task_history)
    
    async def learn_from_feedback(
        self,
        task_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """
        Learn from feedback (for adaptive agents)
        
        Args:
            task_id: Task ID
            feedback: Feedback data
        """
        self.logger.info(f"Received feedback for task {task_id}")
        # Subclasses can implement adaptive learning here
        pass
    
    def reset(self) -> None:
        """Reset agent state"""
        self.status = AgentStatus.IDLE
        self.task_history.clear()
        self.logger.info(f"Agent {self.agent_id} reset")


class AgentSkill(ABC):
    """
    Base class for agent skills
    Skills are reusable capabilities that agents can execute
    """
    
    def __init__(self, skill_id: str, skill_name: str):
        self.skill_id = skill_id
        self.skill_name = skill_name
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute skill"""
        pass
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate skill parameters"""
        pass


class AgentMemory:
    """
    Memory system for agents to store and retrieve information
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: Dict[str, Any] = {}
    
    def store_short_term(self, data: Dict[str, Any]) -> None:
        """Store in short-term memory"""
        self.short_term.append(data)
        if len(self.short_term) > self.max_size:
            self.short_term.pop(0)
    
    def store_long_term(self, key: str, data: Any) -> None:
        """Store in long-term memory"""
        self.long_term[key] = data
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from long-term memory"""
        return self.long_term.get(key)
    
    def search_short_term(
        self,
        filter_fn: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """Search short-term memory with filter"""
        return [item for item in self.short_term if filter_fn(item)]
