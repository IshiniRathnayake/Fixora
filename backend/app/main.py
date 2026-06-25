from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, alerts, auth, dashboard, diagnostics, enterprise, logs
from app.config import get_settings
from app.startup import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as exc:
        print(f"Startup init warning: {exc}")
    yield


app = FastAPI(
    title="Fixora API",
    description=(
        "Multi-Agent AI-Based Automated Administrative System "
        "for Enterprise Business Operations"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(diagnostics.router, prefix="/api/v1")
app.include_router(enterprise.router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "fixora-api"}
