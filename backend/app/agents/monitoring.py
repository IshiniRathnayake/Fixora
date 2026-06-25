"""Monitoring Agent — perception layer (FR1)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.config import get_settings
from app.services.anomaly import AnomalyDetectionService
from app.services.log_parser import LogParserService


class MonitoringAgent(BaseAgent):
    name = "monitoring"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.parser = LogParserService()
        self.detector = AnomalyDetectionService(
            contamination=self.settings.anomaly_contamination
        )

    async def run(self, context: AgentContext) -> AgentResult:
        started = datetime.utcnow()
        logs = context.log_window

        if not logs:
            completed = datetime.utcnow()
            return AgentResult(
                agent_name=self.name,
                status="completed",
                output={"alerts": [], "anomaly_count": 0},
                duration_ms=int((completed - started).total_seconds() * 1000),
                started_at=started,
                completed_at=completed,
            )

        df = pd.DataFrame(logs)
        features = LogParserService.build_feature_matrix(df)
        is_anomaly, scores = self.detector.fit_detect(features)

        anomalies: list[dict] = []
        alerts: list[dict] = []
        for idx, row in df.iterrows():
            if not is_anomaly[idx]:
                continue
            entry = {
                **row.to_dict(),
                "anomaly_score": float(scores[idx]),
                "is_anomaly": True,
                "log_index": int(idx),
            }
            anomalies.append(entry)
            severity = "critical" if row.get("level") in ("FATAL", "ERROR") else "high"
            alerts.append(
                {
                    "severity": severity,
                    "title": f"Anomaly detected: {row.get('level', 'LOG')}",
                    "summary": str(row.get("message", ""))[:500],
                    "log_index": int(idx),
                }
            )

        context.anomalies = anomalies
        if alerts:
            context.alert = alerts[0]

        completed = datetime.utcnow()
        return AgentResult(
            agent_name=self.name,
            status="completed",
            output={
                "anomaly_count": len(anomalies),
                "alerts": alerts,
                "total_logs": len(logs),
            },
            duration_ms=int((completed - started).total_seconds() * 1000),
            started_at=started,
            completed_at=completed,
        )
