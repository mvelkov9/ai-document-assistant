from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = Field(default="AI Document Assistant")
    app_env: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = Field(default="sqlite:///./docassist.db")
    secret_key: str = Field(default="change-me")
    access_token_expire_minutes: int = Field(default=60)
    max_upload_size_mb: int = Field(default=15)

    minio_endpoint: str = Field(default="localhost:9000")
    minio_bucket: str = Field(default="documents")
    minio_secure: bool = Field(default=False)
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")

    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    gemini_api_key: str | None = Field(default=None)
    gemini_model: str = Field(default="gemini-2.0-flash")
    groq_api_key: str | None = Field(default=None)
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    summary_max_chars: int = Field(default=6000)

    @field_validator("openai_api_key", "gemini_api_key", "groq_api_key", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def _validate_production_settings(s: Settings) -> None:
    if s.app_env != "development" and s.secret_key == "change-me":
        raise RuntimeError("SECRET_KEY must be changed from the default in non-development environments")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    _validate_production_settings(s)
    return s
