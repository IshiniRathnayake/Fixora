import time

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.api.deps import CurrentUser, DbSession
from app.models.entities import NLQuery
from app.schemas.api import NLQueryRequest, NLQueryResponse, PipelineRequest
from app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/agents", tags=["Multi-Agent Pipeline"])


class AnalyzeRequest(BaseModel):
    limit: int = Field(default=500, ge=10, le=5000)
    question: str | None = None


@router.post("/analyze")
async def analyze_stored_logs(
    body: AnalyzeRequest,
    user: CurrentUser,
    db: DbSession,
) -> dict:
    """Load logs from DB, run Monitoring → Analysis pipeline, persist alerts & diagnostics."""
    service = PipelineService(db)
    return await service.analyze_stored_logs(
        limit=body.limit,
        question=body.question,
        user_id=user.id,
    )


@router.post("/pipeline")
async def run_pipeline(
    body: PipelineRequest,
    user: CurrentUser,
    db: DbSession,
) -> dict:
    """Run pipeline on client-supplied log window (e.g. offline batch)."""
    service = PipelineService(db)
    if not body.logs:
        return await service.analyze_stored_logs(
            question=body.question,
            user_id=user.id,
        )

    orchestrator = AgentOrchestrator(db)
    started = time.perf_counter()
    if body.question:
        result = await orchestrator.run_full_diagnostic_query(body.question, body.logs)
        pipeline = result["pipeline"]
        nl = result.get("query")
    else:
        pipeline = await orchestrator.run_monitoring_pipeline(body.logs)
        nl = None

    total_ms = int((time.perf_counter() - started) * 1000)
    persisted = service._persist(pipeline, body.logs, total_ms, user.id, nl)
    service._record_health_metrics(pipeline)
    return {**pipeline, "persisted": persisted, "total_latency_ms": total_ms, "nl_query": nl}


@router.post("/query", response_model=NLQueryResponse)
async def natural_language_query(
    body: NLQueryRequest,
    user: CurrentUser,
    db: DbSession,
) -> NLQueryResponse:
    orchestrator = AgentOrchestrator(db)
    started = time.perf_counter()
    result = await orchestrator.run_nl_query(body.question)
    latency = int((time.perf_counter() - started) * 1000)
    output = result["output"]

    record = NLQuery(
        user_id=user.id,
        natural_language=body.question,
        generated_sql=output.get("generated_sql"),
        is_valid_sql=output.get("is_valid_sql", False),
        result_row_count=output.get("row_count"),
        latency_ms=latency,
        error_message=output.get("error"),
    )
    db.add(record)
    db.commit()

    return NLQueryResponse(
        natural_language=body.question,
        generated_sql=output.get("generated_sql"),
        is_valid_sql=output.get("is_valid_sql", False),
        rows=output.get("rows", []),
        row_count=output.get("row_count", 0),
        latency_ms=latency,
        error=output.get("error"),
    )
