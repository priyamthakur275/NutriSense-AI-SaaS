from enum import Enum
from functools import lru_cache

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    """Central application configuration, sourced from environment variables.

    All fields keep their original names/defaults from the initial scaffold
    for backward compatibility with existing imports (`app.core.config.settings`).
    New fields are additive.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    # --- App ---
    PROJECT_NAME: str = "NutriSense AI"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # --- Security ---
    SECRET_KEY: str = "change-this-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    # --- Account lockout policy ---
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    # --- Rate limiting (see app/core/rate_limit.py) ---
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 3

    # --- Database ---
    DATABASE_URL: str = "postgresql://nutrisense:nutrisense@localhost:5432/nutrisense"
    # Pool tuning — ignored automatically for SQLite (NullPool), applied for Postgres.
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800  # seconds; recycle stale connections every 30 min
    DATABASE_ECHO: bool = False

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Observability ---
    METRICS_ENABLED: bool = True

    # --- AI / LLM providers ---
    # `AI_PROVIDER` selects the primary provider; `AI_FALLBACK_PROVIDERS` is
    # an ordered failover list tried if the primary raises. Both API keys
    # are optional at the settings level (a deployment might only configure
    # one provider) — the provider factory, not this class, decides whether
    # a requested provider is actually usable given what's configured.
    AI_PROVIDER: str = "gemini"
    AI_FALLBACK_PROVIDERS: list[str] = Field(default_factory=lambda: ["openai"])
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2
    AI_CACHE_TTL_SECONDS: int = 300

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def _normalize_environment(cls, value: object) -> object:
        if isinstance(value, str):
            return value.lower()
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    return json.loads(value)
                except Exception:
                    pass
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @computed_field  # type: ignore[misc]
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @computed_field  # type: ignore[misc]
    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    def model_post_init(self, __context: object) -> None:
        """Fail fast on insecure/invalid production configuration — a
        misconfigured production deploy should refuse to start rather than
        run in a silently weakened state."""
        if not self.is_production:
            return

        errors: list[str] = []

        if self.SECRET_KEY == "change-this-secret-in-production":
            errors.append("SECRET_KEY must be overridden — refusing to start with the dev default")
        if len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters in production")
        if self.is_sqlite:
            errors.append("SQLite is a development-only database; DATABASE_URL must point to PostgreSQL")
        if self.DEBUG:
            errors.append("DEBUG must be false in production")
        if any(origin == "*" for origin in self.CORS_ORIGINS):
            errors.append("CORS_ORIGINS must not contain a wildcard '*' in production")
        if not self.CORS_ORIGINS:
            errors.append("CORS_ORIGINS must not be empty in production")

        if errors:
            raise ValueError(
                "Invalid production configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
