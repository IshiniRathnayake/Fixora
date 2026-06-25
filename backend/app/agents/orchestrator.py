"""
LangChain-style orchestration layer.

Routes anomaly signals: Monitoring → Analysis → (optional) Data Retrieval.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.analysis import AnalysisDiagnosticAgent
from app.agents.base import AgentContext, AgentResult
from app.agents.data_retrieval import DataRetrievalAgent
from app.agents.monitoring import MonitoringAgent

DEFAULT_SCHEMA_DDL = """
TABLE orders (id, order_ref, customer_name, status, total_amount, created_at);
TABLE inventory (id, sku, product_name, quantity, updated_at);
TABLE log_entries (id, source_id, logged_at, level, message, is_anomaly, anomaly_score);
TABLE alerts (id, severity, title, summary, status, detected_at);
TABLE health_metrics (id, metric_name, metric_value, unit, recorded_at);
"""


class AgentOrchestrator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.monitoring = MonitoringAgent()
        self.analysis = AnalysisDiagnosticAgent()
        self.data_retrieval = DataRetrievalAgent(db)

    async def run_monitoring_pipeline(
        self,
        log_window: list[dict],
        *,
        schema_ddl: str = DEFAULT_SCHEMA_DDL,
    ) -> dict:
        context = AgentContext(
            trigger_type="pipeline",
            log_window=log_window,
            schema_ddl=schema_ddl,
        )
        results: list[AgentResult] = []

        monitor_result = await self.monitoring.run(context)
        results.append(monitor_result)

        if context.anomalies or context.alert:
            analysis_result = await self.analysis.run(context)
            results.append(analysis_result)

        return {
            "context": {
                "anomaly_count": len(context.anomalies),
                "alert": context.alert,
                "diagnostic": context.diagnostic,
            },
            "agent_runs": [
                {
                    "agent": r.agent_name,
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                    "output": r.output,
                }
                for r in results
            ],
        }

    async def run_nl_query(self, question: str, *, schema_ddl: str = DEFAULT_SCHEMA_DDL) -> dict:
        context = AgentContext(
            trigger_type="user_query",
            nl_query=question,
            schema_ddl=schema_ddl,
        )
        result = await self.data_retrieval.run(context)
        return {
            "agent": result.agent_name,
            "status": result.status,
            "duration_ms": result.duration_ms,
            "output": result.output,
        }

    async def run_full_diagnostic_query(
        self,
        question: str,
        log_window: list[dict],
    ) -> dict:
        """Use case from Section 4.3: NL question + active monitoring pipeline."""
        pipeline = await self.run_monitoring_pipeline(log_window)
        nl = await self.run_nl_query(question)
        return {"pipeline": pipeline, "query": nl}
