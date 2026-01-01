"""
Base Agent Class

Provides abstract interface for all specialized agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Standardized agent execution result"""

    agent_name: str
    status: str  # success, failure, partial
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    steps: List[Dict[str, Any]] = field(default_factory=list)

    def add_step(self, step_name: str, result: Any, duration: float = 0.0):
        """Log an execution step"""
        self.steps.append({
            'name': step_name,
            'result': result,
            'duration': duration,
            'timestamp': datetime.now()
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'agent_name': self.agent_name,
            'status': self.status,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'steps': self.steps
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Agents are specialized components that perform specific knowledge work tasks.
    Each agent has access to the knowledge base and can coordinate with other agents.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"Agent.{name}")

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's primary task.

        Args:
            task: Dictionary containing task parameters

        Returns:
            AgentResult with execution status and data
        """
        pass

    def validate_task(self, task: Dict[str, Any], required_keys: List[str]) -> bool:
        """
        Validate that task contains required parameters.

        Args:
            task: Task dictionary
            required_keys: List of required key names

        Returns:
            True if valid, False otherwise
        """
        missing = [k for k in required_keys if k not in task]
        if missing:
            self.logger.error(f"Missing required task parameters: {missing}")
            return False
        return True

    def log_step(self, step_name: str, details: str = ""):
        """Log an execution step"""
        self.logger.info(f"[{self.name}] {step_name}: {details}")

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
