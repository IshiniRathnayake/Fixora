from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.entities import Alert
from app.schemas.api import AlertOut

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=list[AlertOut])
def list_alerts(user: CurrentUser, db: DbSession, status: str | None = None) -> list[AlertOut]:
    q = db.query(Alert).order_by(Alert.detected_at.desc())
    if status:
        q = q.filter(Alert.status == status)
    return [AlertOut.model_validate(a) for a in q.limit(100).all()]


@router.patch("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: int, user: AdminUser, db: DbSession) -> AlertOut:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "acknowledged"
    alert.acknowledged_by = user.id
    db.commit()
    db.refresh(alert)
    return AlertOut.model_validate(alert)
