from datetime import datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.models.entities import AgentRun, Alert, Diagnostic, HealthMetric, LogEntry, NLQuery
from app.schemas.api import AlertOut, DashboardSummary, DiagnosticOut, HealthMetricOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(user: CurrentUser, db: DbSession) -> DashboardSummary:
    since = datetime.utcnow() - timedelta(hours=24)

    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar() or 0
    anomalies_24h = (
        db.query(func.count(LogEntry.id))
        .filter(LogEntry.is_anomaly.is_(True), LogEntry.logged_at >= since)
        .scalar()
        or 0
    )
    avg_latency = db.query(func.avg(NLQuery.latency_ms)).scalar() or 0.0

    recent_alerts = (
        db.query(Alert).order_by(Alert.detected_at.desc()).limit(5).all()
    )
    recent_diagnostics = (
        db.query(Diagnostic).order_by(Diagnostic.created_at.desc()).limit(5).all()
    )
    agent_activity = (
        db.query(AgentRun)
        .order_by(AgentRun.started_at.desc())
        .limit(10)
        .all()
    )

    health_score = _compute_health_score(db, open_alerts, anomalies_24h)

    return DashboardSummary(
        open_alerts=open_alerts,
        anomalies_24h=anomalies_24h,
        avg_response_ms=float(avg_latency),
        system_health_score=health_score,
        recent_alerts=[AlertOut.model_validate(a) for a in recent_alerts],
        recent_diagnostics=[DiagnosticOut.model_validate(d) for d in recent_diagnostics],
        agent_activity=[
            {
                "agent": r.agent_name,
                "status": r.status,
                "duration_ms": r.duration_ms,
                "started_at": r.started_at.isoformat() if r.started_at else None,
            }
            for r in agent_activity
        ],
    )


@router.get("/metrics", response_model=list[HealthMetricOut])
def health_metrics(user: CurrentUser, db: DbSession) -> list[HealthMetricOut]:
    rows = (
        db.query(HealthMetric)
        .order_by(HealthMetric.recorded_at.desc())
        .limit(50)
        .all()
    )
    return [
        HealthMetricOut(
            metric_name=r.metric_name,
            metric_value=float(r.metric_value),
            unit=r.unit,
            recorded_at=r.recorded_at,
        )
        for r in rows
    ]


def _compute_health_score(db: Session, open_alerts: int, anomalies: int) -> float:
    base = 100.0
    base -= min(open_alerts * 5, 40)
    base -= min(anomalies * 2, 30)
    error_count = (
        db.query(func.count(LogEntry.id))
        .filter(LogEntry.level.in_(["ERROR", "FATAL"]))
        .scalar()
        or 0
    )
    base -= min(error_count * 0.5, 20)
    return max(0.0, min(100.0, base))
