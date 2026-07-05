"""Office support issue resolution API."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.agents.support_context import SupportContext
from app.agents.support_orchestrator import SupportOrchestrator
from app.api.deps import AdminUser, CurrentUser, DbSession, OptionalUser
from app.models.entities import SupportTicket
from app.schemas.api import (
    IssueAnalyzeRequest,
    IssueAnalyzeResponse,
    ResolutionFeedback,
    SupportTicketOut,
    TicketStatusUpdate,
)

router = APIRouter(prefix="/support", tags=["support"])
logger = logging.getLogger("fixora.agents")


@router.post("/analyze", response_model=IssueAnalyzeResponse)
async def analyze_issue(
    body: IssueAnalyzeRequest,
    db: DbSession,
    user: OptionalUser = None,
) -> IssueAnalyzeResponse:
    """Run multi-agent issue resolution workflow (Groq + Gemini)."""
    logger.info(
        "API /support/analyze | user=%s | source=%s",
        user.email if user else "anonymous",
        body.source,
    )
    ctx = SupportContext(
        description=body.description.strip(),
        source=body.source,
        user_id=user.id if user else None,
        page_url=body.page_url,
        page_title=body.page_title,
        page_error=body.page_error,
        browser=body.browser,
        os_info=body.os_info,
        selected_text=body.selected_text,
    )
    orchestrator = SupportOrchestrator(db)
    result = await orchestrator.resolve(ctx)
    return IssueAnalyzeResponse(**result)


@router.get("/tickets/me", response_model=list[SupportTicketOut])
def my_tickets(db: DbSession, user: CurrentUser) -> list[SupportTicket]:
    return (
        db.query(SupportTicket)
        .filter(SupportTicket.requester_id == user.id)
        .order_by(SupportTicket.created_at.desc())
        .limit(50)
        .all()
    )


@router.get("/tickets/queue", response_model=list[SupportTicketOut])
def ticket_queue(db: DbSession, user: AdminUser) -> list[SupportTicket]:
    return (
        db.query(SupportTicket)
        .filter(SupportTicket.status.in_(["open", "in_progress"]))
        .order_by(SupportTicket.created_at.desc())
        .limit(100)
        .all()
    )


@router.get("/tickets/{ticket_id}", response_model=SupportTicketOut)
def get_ticket(ticket_id: int, db: DbSession, user: CurrentUser) -> SupportTicket:
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if user.role_id != 1 and ticket.requester_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=SupportTicketOut)
def update_ticket_status(
    ticket_id: int,
    body: TicketStatusUpdate,
    db: DbSession,
    user: AdminUser,
) -> SupportTicket:
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = body.status
    if body.status in ("resolved", "closed"):
        from datetime import datetime, timezone

        ticket.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/feedback")
def submit_feedback(body: ResolutionFeedback, db: DbSession, user: OptionalUser = None) -> dict:
    return {
        "status": "received",
        "was_helpful": body.was_helpful,
        "resolved_without_it": body.resolved_without_it,
        "user_id": user.id if user else None,
        "ticket_id": body.ticket_id,
    }
