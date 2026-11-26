from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings, loaded from environment variables and backend/.env."""

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Learning Lab API"
    app_version: str = "0.5.0"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    # Comma-separated list, parsed by cors_origin_list.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    database_url: str = ""

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    # A just-rotated refresh token replayed inside this window (two tabs racing) is rejected
    # without revoking the whole token family. After it, replay is treated as theft.
    refresh_reuse_grace_seconds: int = 10
    refresh_cookie_name: str = "ail_refresh"
    cookie_secure: bool = True
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # Argon2id defaults follow the RFC 9106 low-memory profile (64 MiB, 3 passes, 4 lanes).
    argon2_time_cost: int = 3
    argon2_memory_kib: int = 65536
    argon2_parallelism: int = 4

    login_max_failures: int = 5
    login_window_seconds: int = 900

    # AI assistants. The key is a SecretStr so it never appears in logs or tracebacks.
    # Check the current model names at https://platform.openai.com/docs/models and set OPENAI_MODEL accordingly.
    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    ai_timeout_seconds: int = 45
    ai_max_output_tokens: int = 900
    ai_daily_request_limit: int = 40
    ai_daily_token_limit: int = 100_000

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def docs_enabled(self) -> bool:
        return self.environment != "production"

    @property
    def refresh_cookie_path(self) -> str:
        return f"{self.api_prefix}/auth"

    @property
    def ai_configured(self) -> bool:
        return bool(self.openai_api_key.get_secret_value().strip())

    def assert_production_ready(self) -> None:
        """Fail fast at startup when a production deployment is misconfigured."""
        if self.environment != "production":
            return
        problems: list[str] = []
        if len(self.jwt_secret) < 32:
            problems.append("JWT_SECRET must be at least 32 characters")
        if not self.database_url:
            problems.append("DATABASE_URL is required")
        if not self.cookie_secure:
            problems.append("COOKIE_SECURE must be true")
        if problems:
            raise RuntimeError("Invalid production configuration: " + "; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()
