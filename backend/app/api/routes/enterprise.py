"""Simulated enterprise application (orders / inventory) for prototype integration."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.entities import LogEntry
from app.services.log_parser import LogParserService
from sqlalchemy import text

router = APIRouter(prefix="/enterprise", tags=["Enterprise App"])


@router.get("/orders")
def list_orders(user: CurrentUser, db: DbSession) -> list[dict]:
    result = db.execute(
        text("SELECT id, order_ref, customer_name, status, total_amount, created_at FROM orders ORDER BY id DESC LIMIT 50")
    )
    cols = result.keys()
    return [dict(zip(cols, row)) for row in result.fetchall()]


@router.get("/inventory")
def list_inventory(user: CurrentUser, db: DbSession) -> list[dict]:
    result = db.execute(
        text("SELECT id, sku, product_name, quantity, updated_at FROM inventory ORDER BY sku")
    )
    cols = result.keys()
    return [dict(zip(cols, row)) for row in result.fetchall()]


@router.post("/orders/{order_id}/process")
def process_order(order_id: int, user: AdminUser, db: DbSession) -> dict:
    """Simulate order processing — may emit ERROR logs on failure."""
    row = db.execute(
        text("SELECT id, order_ref, status FROM orders WHERE id = :id"),
        {"id": order_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")

    order_ref = row[1]
    status = row[2]
    parser = LogParserService()

    if status == "failed":
        msg = f"ERROR Order {order_ref} processing failed — prior failure state"
        level = "ERROR"
    elif status == "processing":
        msg = f"WARN Slow transaction on order {order_ref} — lock wait detected"
        level = "WARN"
        db.execute(text("UPDATE orders SET status = 'completed' WHERE id = :id"), {"id": order_id})
    else:
        msg = f"INFO Order {order_ref} processed successfully"
        level = "INFO"

    parsed = parser.parse_line(msg)
    db.add(
        LogEntry(
            source_id=3,
            logged_at=datetime.utcnow(),
            level=parsed.level if parsed.level else level,
            message=parsed.message,
            template_id=parsed.template_id,
            raw_line=msg,
        )
    )
    db.commit()
    return {"order_id": order_id, "log_message": msg, "level": level}
