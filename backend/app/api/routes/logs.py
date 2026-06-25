from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.entities import LogEntry
from app.services.log_parser import LogParserService

router = APIRouter(prefix="/logs", tags=["Log Monitoring"])


@router.get("/")
def list_logs(
    user: CurrentUser,
    db: DbSession,
    limit: int = 100,
    anomalies_only: bool = False,
) -> list[dict]:
    q = db.query(LogEntry).order_by(LogEntry.logged_at.desc())
    if anomalies_only:
        q = q.filter(LogEntry.is_anomaly.is_(True))
    rows = q.limit(min(limit, 500)).all()
    return [
        {
            "id": r.id,
            "logged_at": r.logged_at.isoformat() if r.logged_at else None,
            "level": r.level,
            "message": r.message[:300],
            "is_anomaly": r.is_anomaly,
            "anomaly_score": r.anomaly_score,
        }
        for r in rows
    ]


@router.post("/ingest")
async def ingest_log_file(
    user: AdminUser,
    db: DbSession,
    file: UploadFile = File(...),
    source_id: int = 3,
) -> dict:
    """Ingest a log file, parse with Drain3, and store entries (FR1)."""
    content = (await file.read()).decode("utf-8", errors="replace")
    parser = LogParserService()
    stored = 0
    for line in content.splitlines():
        if not line.strip():
            continue
        parsed = parser.parse_line(line)
        db.add(
            LogEntry(
                source_id=source_id,
                logged_at=parsed.logged_at,
                level=parsed.level,
                message=parsed.message,
                template_id=parsed.template_id,
                raw_line=line[:4000],
            )
        )
        stored += 1
    db.commit()
    return {"filename": file.filename, "entries_stored": stored}


@router.post("/analyze")
async def analyze_logs(user: CurrentUser, db: DbSession, question: str | None = None) -> dict:
    """Analyze all stored logs with the multi-agent pipeline."""
    from app.services.pipeline_service import PipelineService

    service = PipelineService(db)
    return await service.analyze_stored_logs(question=question, user_id=user.id)


@router.post("/ingest/sample")
def ingest_sample_logs(user: AdminUser, db: DbSession) -> dict:
    """Load bundled sample logs for demo without external files."""
    sample_path = Path(__file__).resolve().parents[3] / "data" / "logs" / "sample_app.log"
    if not sample_path.exists():
        return {"entries_stored": 0, "message": "Sample file not found"}

    parser = LogParserService()
    stored = 0
    with sample_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            parsed = parser.parse_line(line)
            db.add(
                LogEntry(
                    source_id=3,
                    logged_at=datetime.utcnow(),
                    level=parsed.level,
                    message=parsed.message,
                    template_id=parsed.template_id,
                    raw_line=line[:4000],
                )
            )
            stored += 1
    db.commit()
    return {"entries_stored": stored, "source": str(sample_path)}
