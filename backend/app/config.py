"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for BhuSanket backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "BhuSanket"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-secure-random-string-in-production"
    api_prefix: str = "/api/v1"

    # --- Database ---
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "bhusanket"
    postgres_user: str = "bhusanket_user"
    postgres_password: str = "bhusanket_dev_password"
    database_url_env: str | None = Field(default=None, alias="DATABASE_URL")

    @property
    def database_url(self) -> str:
        if self.database_url_env:
            if self.database_url_env.startswith("postgresql://"):
                return self.database_url_env.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.database_url_env
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        if self.database_url_env:
            return self.database_url_env
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --- Redis ---
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_url_env: str | None = Field(default=None, alias="REDIS_URL")

    @property
    def redis_url(self) -> str:
        if self.redis_url_env:
            return self.redis_url_env
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_broker_url(self) -> str:
        if self.redis_url_env:
            url = self.redis_url_env
            if url.startswith("rediss://") and "ssl_cert_reqs=" not in url:
                url += "&ssl_cert_reqs=CERT_NONE" if "?" in url else "?ssl_cert_reqs=CERT_NONE"
            return url
        return f"redis://{self.redis_host}:{self.redis_port}/1"

    @property
    def celery_result_backend(self) -> str:
        if self.redis_url_env:
            url = self.redis_url_env
            if url.startswith("rediss://") and "ssl_cert_reqs=" not in url:
                url += "&ssl_cert_reqs=CERT_NONE" if "?" in url else "?ssl_cert_reqs=CERT_NONE"
            return url
        return f"redis://{self.redis_host}:{self.redis_port}/2"

    # --- JWT ---
    jwt_secret_key: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # --- Object Storage ---
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "bhusanket-artifacts"

    # --- Model Defaults ---
    hazard_bucket_width_days: int = 7
    risk_velocity_window_days: int = 14
    risk_stable_threshold: float = 5.0
    risk_rising_threshold: float = 15.0
    priority_weight_risk: float = 0.35
    priority_weight_urgency: float = 0.25
    priority_weight_impact: float = 0.25
    priority_weight_actionability: float = 0.15
    actionability_monitor_threshold: float = 0.3
    deadline_risk_green: float = 0.2
    deadline_risk_amber: float = 0.5
    deadline_risk_red: float = 0.8

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings instance."""
    return Settings()
