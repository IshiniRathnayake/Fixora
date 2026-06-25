"""Analysis & Diagnostic Agent — reasoning layer (FR2)."""

from __future__ import annotations

from datetime import datetime

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.config import get_settings
from app.services.llm import GrokClient, parse_diagnostic_json


class AnalysisDiagnosticAgent(BaseAgent):
    name = "analysis"

    def __init__(self) -> None:
        self.llm = GrokClient()
        self.settings = get_settings()

    async def run(self, context: AgentContext) -> AgentResult:
        started = datetime.utcnow()

        if not context.anomalies and not context.alert:
            completed = datetime.utcnow()
            return AgentResult(
                agent_name=self.name,
                status="completed",
                output={"diagnostic": None, "message": "No anomalies to analyse"},
                duration_ms=int((completed - started).total_seconds() * 1000),
                started_at=started,
                completed_at=completed,
            )

        sample_logs = context.anomalies[:20] or [context.alert]
        system_prompt = (
            "You are an enterprise IT diagnostic assistant. "
            "Analyse log anomalies and respond ONLY with valid JSON containing keys: "
            "root_cause, explanation, remediation, confidence (0-1). "
            "Use plain English understandable by non-technical staff."
        )
        user_prompt = (
            f"Schema context:\n{context.schema_ddl[:2000]}\n\n"
            f"Anomalies:\n{sample_logs}\n\n"
            "Provide root cause hypothesis and actionable remediation."
        )

        raw = await self.llm.complete(system_prompt, user_prompt)
        parsed = parse_diagnostic_json(raw)

        diagnostic = {
            "root_cause": parsed.get("root_cause", "Unknown"),
            "explanation": parsed.get("explanation", raw[:1000]),
            "remediation": parsed.get("remediation", ""),
            "confidence": float(parsed.get("confidence", 0.5)),
            "model_version": self.settings.xai_model,
        }
        context.diagnostic = diagnostic

        completed = datetime.utcnow()
        return AgentResult(
            agent_name=self.name,
            status="completed",
            output={"diagnostic": diagnostic},
            duration_ms=int((completed - started).total_seconds() * 1000),
            started_at=started,
            completed_at=completed,
        )
