"""Orchestrator agent: coordinate phase-0 placeholder pipeline."""

from __future__ import annotations

from backend.agents.compensation_agent import CompensationAgent
from backend.agents.constraint_agent import ConstraintAgent
from backend.agents.tradeoff_agent import TradeoffAgent
from shared.project_state import ProjectState


class OrchestratorAgent:
    """Runs lightweight constraint -> compensation -> tradeoff sequence."""

    def __init__(self) -> None:
        self.constraint_agent = ConstraintAgent()
        self.compensation_agent = CompensationAgent()
        self.tradeoff_agent = TradeoffAgent()

    def run(self, project: ProjectState) -> ProjectState:
        _ = self.constraint_agent.run(project)
        options = self.compensation_agent.run(project)
        project.mitigation_options = self.tradeoff_agent.run(project, options)
        return project
