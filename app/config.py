import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, Field, field_validator


class Settings(BaseSettings):
    # General App Info
    APP_NAME: str = Field("Smart API Monitor", env="APP_NAME")
    VERSION: str = Field("1.0.0", env="VERSION")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")  # dev. | staging | prod.

    # Security
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALLOWED_HOSTS: list[AnyHttpUrl] = Field(default_factory=list, env="ALLOWED_HOSTS")

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # Optional External Services
    REDIS_URL: str | None = Field(None, env="REDIS_URL")
    SENTRY_DSN: str | None = Field(None, env="SENTRY_DSN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore undefined env vars
    )

    # Extra validation
    @field_validator("ENVIRONMENT")
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
