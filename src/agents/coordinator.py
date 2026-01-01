"""
Agent Coordinator

Orchestrates multi-agent workflows with dependency management and parallel execution.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""
    agent_name: str
    task: Dict[str, Any]
    dependencies: List[str] = None  # Names of steps this depends on

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class AgentCoordinator:
    """
    Coordinates execution of multiple agents to accomplish complex workflows.

    Features:
    - Dependency resolution
    - Parallel execution where possible
    - Result aggregation
    - Error handling and recovery
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentCoordinator")

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")

    def execute_workflow(
        self,
        workflow_name: str,
        steps: List[WorkflowStep],
        max_workers: int = 3
    ) -> Dict[str, AgentResult]:
        """
        Execute a workflow with multiple agent steps.

        Args:
            workflow_name: Name of the workflow for logging
            steps: List of workflow steps to execute
            max_workers: Maximum parallel agent executions

        Returns:
            Dictionary mapping step names to AgentResults
        """
        self.logger.info(f"Starting workflow: {workflow_name}")
        start_time = time.time()

        results: Dict[str, AgentResult] = {}
        completed: set = set()
        pending = {f"{step.agent_name}_{i}": step for i, step in enumerate(steps)}

        while pending:
            # Find steps ready to execute (all dependencies met)
            ready = [
                (name, step) for name, step in pending.items()
                if all(dep in completed for dep in step.dependencies)
            ]

            if not ready:
                # No steps ready - check for circular dependencies
                self.logger.error("Circular dependency detected or missing agent")
                break

            # Execute ready steps in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {}
                for step_name, step in ready:
                    agent = self.agents.get(step.agent_name)
                    if not agent:
                        self.logger.error(f"Agent not found: {step.agent_name}")
                        results[step_name] = AgentResult(
                            agent_name=step.agent_name,
                            status="failure",
                            errors=[f"Agent {step.agent_name} not registered"]
                        )
                        continue

                    # Add results from dependencies to task context
                    step.task['dependency_results'] = {
                        dep: results.get(dep) for dep in step.dependencies
                    }

                    future = executor.submit(self._execute_step, agent, step)
                    futures[future] = step_name

                # Collect results
                for future in as_completed(futures):
                    step_name = futures[future]
                    try:
                        result = future.result()
                        results[step_name] = result
                        completed.add(step_name)
                        self.logger.info(
                            f"Completed step {step_name}: {result.status}"
                        )
                    except Exception as e:
                        self.logger.error(f"Step {step_name} failed: {e}")
                        results[step_name] = AgentResult(
                            agent_name=pending[step_name].agent_name,
                            status="failure",
                            errors=[str(e)]
                        )

            # Remove completed steps from pending
            for step_name in list(pending.keys()):
                if step_name in completed or step_name in results:
                    pending.pop(step_name, None)

        duration = time.time() - start_time
        self.logger.info(
            f"Workflow {workflow_name} completed in {duration:.2f}s. "
            f"Success: {sum(1 for r in results.values() if r.status == 'success')}/{len(results)}"
        )

        return results

    def _execute_step(self, agent: BaseAgent, step: WorkflowStep) -> AgentResult:
        """Execute a single workflow step"""
        try:
            result = agent.execute(step.task)
            return result
        except Exception as e:
            self.logger.error(f"Agent {agent.name} execution failed: {e}")
            return AgentResult(
                agent_name=agent.name,
                status="failure",
                errors=[str(e)]
            )

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names"""
        return list(self.agents.keys())
