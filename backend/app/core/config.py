from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AWS Guardian"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # AWS Settings
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Watchdog Engine Defaults (Deterministic Rules)
    DEFAULT_IDLE_HOURS_THRESHOLD: int = 4
    DEFAULT_CPU_IDLE_PERCENT: float = 2.5

    # Safety Protection
    PROTECTED_TAG_KEY: str = "Environment"
    PROTECTED_TAG_VALUE: str = "production"

    # AI Intelligence Layer
    AI_PROVIDER: str = "local_heuristic"  # Options: "local_heuristic", "openai"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()