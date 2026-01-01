"""
Multi-Agent Framework for GPTBuddyAI

Provides orchestration and specialized agents for complex knowledge work automation.
"""

from .base_agent import BaseAgent, AgentResult
from .coordinator import AgentCoordinator
from .compliance_agent import ComplianceAgent
from .research_agent import ResearchAgent
from .synthesis_agent import SynthesisAgent

__all__ = [
    'BaseAgent',
    'AgentResult',
    'AgentCoordinator',
    'ComplianceAgent',
    'ResearchAgent',
    'SynthesisAgent',
]
