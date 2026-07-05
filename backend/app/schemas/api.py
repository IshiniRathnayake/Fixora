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


class IssueAnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=4000)
    source: str = Field(default="web", pattern="^(web|extension)$")
    page_url: Optional[str] = Field(default=None, max_length=512)
    page_title: Optional[str] = Field(default=None, max_length=255)
    page_error: Optional[str] = Field(default=None, max_length=2000)
    browser: Optional[str] = Field(default=None, max_length=128)
    os_info: Optional[str] = Field(default=None, max_length=128)
    selected_text: Optional[str] = Field(default=None, max_length=2000)


class IssueAnalyzeResponse(BaseModel):
    resolution: dict[str, Any]
    category: str
    priority: str
    confidence: float
    can_self_resolve: bool
    knowledge_used: list[dict[str, Any]]
    escalation: dict[str, Any]
    ticket: Optional[dict[str, Any]] = None
    workflow: dict[str, Any]


class SupportTicketOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    source: str
    page_url: Optional[str]
    ai_summary: Optional[str]
    suggested_resolution: Optional[str]
    model_confidence: Optional[float]
    assigned_team: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(open|in_progress|resolved|closed)$")


class ResolutionFeedback(BaseModel):
    ticket_id: Optional[int] = None
    was_helpful: bool
    resolved_without_it: bool
    feedback_text: Optional[str] = Field(default=None, max_length=1000)
