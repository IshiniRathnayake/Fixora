from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbSession
from app.models.entities import Diagnostic
from app.schemas.api import DiagnosticOut

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])


@router.get("/", response_model=list[DiagnosticOut])
def list_diagnostics(user: CurrentUser, db: DbSession, limit: int = 20) -> list[DiagnosticOut]:
    rows = db.query(Diagnostic).order_by(Diagnostic.created_at.desc()).limit(min(limit, 100)).all()
    return [DiagnosticOut.model_validate(d) for d in rows]


@router.get("/{diagnostic_id}", response_model=DiagnosticOut)
def get_diagnostic(diagnostic_id: int, user: CurrentUser, db: DbSession) -> DiagnosticOut:
    row = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return DiagnosticOut.model_validate(row)
