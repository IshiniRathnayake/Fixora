from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentContext:
    """Shared context passed between agents in the LangChain-style pipeline."""

    trigger_type: str = "pipeline"
    log_window: list[dict[str, Any]] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)
    alert: dict[str, Any] | None = None
    diagnostic: dict[str, Any] | None = None
    nl_query: str | None = None
    schema_ddl: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_name: str
    status: str
    output: dict[str, Any]
    duration_ms: int
    started_at: datetime
    completed_at: datetime


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        ...
