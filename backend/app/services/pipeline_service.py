"""Run multi-agent pipeline and persist results to MySQL."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import AgentOrchestrator
from app.models.entities import AgentRun, Alert, Diagnostic, HealthMetric, LogEntry, NLQuery


class PipelineService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.orchestrator = AgentOrchestrator(db)

    def load_logs_from_db(self, limit: int = 500) -> list[dict[str, Any]]:
        rows = (
            self.db.query(LogEntry)
            .order_by(LogEntry.logged_at.desc())
            .limit(limit)
            .all()
        )
        rows.reverse()
        return [
            {
                "id": r.id,
                "level": r.level,
                "message": r.message,
                "template_id": r.template_id or "0",
                "logged_at": r.logged_at.isoformat() if r.logged_at else None,
            }
            for r in rows
        ]

    async def analyze_stored_logs(
        self,
        *,
        limit: int = 500,
        question: str | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        logs = self.load_logs_from_db(limit=limit)
        if not logs:
            return {
                "message": "No logs in database. Ingest sample logs first.",
                "anomaly_count": 0,
                "agent_runs": [],
            }

        started = time.perf_counter()
        if question:
            raw = await self.orchestrator.run_full_diagnostic_query(question, logs)
            pipeline = raw["pipeline"]
            nl_result = raw.get("query")
        else:
            pipeline = await self.orchestrator.run_monitoring_pipeline(logs)
            nl_result = None

        total_ms = int((time.perf_counter() - started) * 1000)
        persisted = self._persist(pipeline, logs, total_ms, user_id, nl_result)
        self._record_health_metrics(pipeline)

        return {
            **pipeline,
            "persisted": persisted,
            "total_latency_ms": total_ms,
            "nl_query": nl_result,
        }

    def _persist(
        self,
        pipeline: dict,
        logs: list[dict],
        total_ms: int,
        user_id: int | None,
        nl_result: dict | None,
    ) -> dict[str, Any]:
        alert_ids: list[int] = []
        diagnostic_id: int | None = None

        for run in pipeline.get("agent_runs", []):
            self.db.add(
                AgentRun(
                    agent_name=run["agent"],
                    trigger_type="pipeline",
                    input_summary=f"{len(logs)} log entries",
                    output_summary=str(run.get("output", ""))[:2000],
                    status=run.get("status", "completed"),
                    duration_ms=run.get("duration_ms"),
                    completed_at=datetime.utcnow(),
                )
            )

        monitor_output = next(
            (r["output"] for r in pipeline.get("agent_runs", []) if r["agent"] == "monitoring"),
            {},
        )
        alerts_data = monitor_output.get("alerts", [])

        anomalous_indices = {a.get("log_index") for a in alerts_data if a.get("log_index") is not None}
        for idx in anomalous_indices:
            if idx >= len(logs):
                continue
            log_id = logs[idx].get("id")
            if not log_id:
                continue
            entry = self.db.query(LogEntry).filter(LogEntry.id == log_id).first()
            if entry:
                entry.is_anomaly = True
                entry.anomaly_score = entry.anomaly_score or 0.85

        for alert_data in alerts_data:
            log_id = None
            idx = alert_data.get("log_index")
            if idx is not None and idx < len(logs):
                log_id = logs[idx].get("id")

            alert = Alert(
                severity=alert_data.get("severity", "high"),
                title=alert_data.get("title", "Anomaly detected"),
                summary=alert_data.get("summary", ""),
                status="open",
                log_entry_id=log_id,
            )
            self.db.add(alert)
            self.db.flush()
            alert_ids.append(alert.id)

        diagnostic = pipeline.get("context", {}).get("diagnostic")
        if diagnostic:
            diag = Diagnostic(
                alert_id=alert_ids[0] if alert_ids else None,
                root_cause=diagnostic["root_cause"],
                explanation=diagnostic["explanation"],
                remediation=diagnostic.get("remediation"),
                confidence=diagnostic.get("confidence"),
                model_version=diagnostic.get("model_version"),
            )
            self.db.add(diag)
            self.db.flush()
            diagnostic_id = diag.id

        if nl_result and user_id:
            output = nl_result.get("output", nl_result)
            self.db.add(
                NLQuery(
                    user_id=user_id,
                    natural_language=output.get("natural_language", ""),
                    generated_sql=output.get("generated_sql"),
                    is_valid_sql=output.get("is_valid_sql", False),
                    result_row_count=output.get("row_count"),
                    latency_ms=nl_result.get("duration_ms"),
                    error_message=output.get("error"),
                )
            )

        self.db.commit()
        return {
            "alerts_created": len(alert_ids),
            "diagnostic_id": diagnostic_id,
            "logs_marked_anomaly": len(anomalous_indices),
        }

    def _record_health_metrics(self, pipeline: dict) -> None:
        ctx = pipeline.get("context", {})
        anomaly_count = ctx.get("anomaly_count", 0)
        score = max(0.0, min(100.0, 100.0 - anomaly_count * 8))
        self.db.add(
            HealthMetric(metric_name="system_health_score", metric_value=score, unit="percent")
        )
        self.db.add(
            HealthMetric(metric_name="anomaly_count", metric_value=float(anomaly_count), unit="count")
        )
        self.db.commit()
