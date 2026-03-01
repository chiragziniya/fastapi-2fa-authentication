from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/authbox"
    db_pool_size: int = 5          # Max persistent connections
    db_max_overflow: int = 10      # Extra connections allowed above pool_size
    db_pool_recycle: int = 300     # Recycle connections after 5 min (Supabase/pgbouncer safe)

    # Server
    port: int = 8000               # Render sets PORT env var automatically
    environment: str = "development"  # "development" | "production"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS
    frontend_url: str = "http://localhost:8080"
    allowed_origins: str = ""  # Comma-separated extra origins (e.g. for production)

    # Email
    mail_mode: str = "console"  # "console" or "smtp"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@example.com"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
