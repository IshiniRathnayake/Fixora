from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "fixora"
    mysql_password: str = "fixora_dev_password"
    mysql_database: str = "fixora"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 480

    xai_api_key: str = ""
    xai_model: str = "grok-2-latest"
    xai_base_url: str = "https://api.x.ai/v1"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    cors_origins: str = "http://localhost:5173,http://localhost:3000,chrome-extension://*"

    log_batch_size: int = 500
    anomaly_contamination: float = 0.05

    # Set true when Docker/MySQL is not available (local dev on Windows)
    use_sqlite: bool = False
    sqlite_path: str = ""

    @property
    def database_url(self) -> str:
        if self.use_sqlite:
            db_file = Path(self.sqlite_path) if self.sqlite_path else _BACKEND_ROOT / "data" / "fixora.db"
            if not db_file.is_absolute():
                db_file = _BACKEND_ROOT / db_file
            db_file.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_file.as_posix()}"
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
