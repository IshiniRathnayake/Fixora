from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, alerts, auth, dashboard, diagnostics, enterprise, logs, support
from app.config import get_settings
from app.startup import init_db

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("fixora.agents").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


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
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"chrome-extension://.*",
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
app.include_router(support.router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": "fixora-api",
        "ai": {
            "groq": bool(settings.groq_api_key),
            "gemini": bool(settings.gemini_api_key),
            "xai": bool(settings.xai_api_key),
        },
    }
