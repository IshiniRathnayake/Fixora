"""Support issue context shared across office-support agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SupportContext:
    """Context for employee issue resolution workflow."""

    description: str
    source: str = "web"  # web | extension
    user_id: int | None = None

    # Captured from extension or web form
    page_url: str | None = None
    page_title: str | None = None
    page_error: str | None = None
    browser: str | None = None
    os_info: str | None = None
    selected_text: str | None = None

    # Agent outputs (filled progressively)
    intake: dict[str, Any] = field(default_factory=dict)
    rule_classification: dict[str, Any] = field(default_factory=dict)
    scenario: dict[str, Any] = field(default_factory=dict)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    context_analysis: dict[str, Any] = field(default_factory=dict)
    resolution: dict[str, Any] = field(default_factory=dict)
    escalation: dict[str, Any] = field(default_factory=dict)
    ticket: dict[str, Any] | None = None

    # Workflow metadata
    agent_runs: list[dict[str, Any]] = field(default_factory=list)
    workflow_phases: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        parts = [f"User issue: {self.description}"]
        if self.page_url:
            parts.append(f"Page URL: {self.page_url}")
        if self.page_title:
            parts.append(f"Page title: {self.page_title}")
        if self.page_error:
            parts.append(f"Visible error: {self.page_error}")
        if self.browser:
            parts.append(f"Browser: {self.browser}")
        if self.os_info:
            parts.append(f"OS: {self.os_info}")
        if self.selected_text:
            parts.append(f"Selected text: {self.selected_text}")
        return "\n".join(parts)
