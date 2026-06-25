from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    severity: str
    title: str
    summary: str
    status: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class DiagnosticOut(BaseModel):
    id: int
    root_cause: str
    explanation: str
    remediation: Optional[str]
    confidence: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthMetricOut(BaseModel):
    metric_name: str
    metric_value: float
    unit: Optional[str]
    recorded_at: datetime


class DashboardSummary(BaseModel):
    open_alerts: int
    anomalies_24h: int
    avg_response_ms: float
    system_health_score: float
    recent_alerts: list[AlertOut]
    recent_diagnostics: list[DiagnosticOut]
    agent_activity: list[dict[str, Any]]


class NLQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


class NLQueryResponse(BaseModel):
    natural_language: str
    generated_sql: Optional[str]
    is_valid_sql: bool
    rows: list[dict[str, Any]]
    row_count: int
    latency_ms: int
    error: Optional[str] = None


class PipelineRequest(BaseModel):
    logs: list[dict[str, Any]] = Field(default_factory=list)
    question: Optional[str] = None
