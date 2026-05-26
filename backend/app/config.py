from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_secret_key: str = "change-me-in-production"
    app_base_url: str = "http://localhost:8080"
    frontend_url: str = "http://localhost:3001"
    database_url: str = "sqlite:///./appsec.db"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "appsec"
    minio_secret_key: str = "appsec_dev_password"
    minio_bucket: str = "appsec-evidence"
    llm_provider: str = "openai_compatible"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "local-dev-key"
    llm_model: str = "qwen35-hauhau-q4:latest"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    llm_timeout_seconds: int = 120
    use_llm_planner: bool = False
    sandbox_mode: str = "docker"
    sandbox_default_network_egress: bool = False
    sandbox_max_cpu: int = 2
    sandbox_max_memory_mb: int = 4096
    sandbox_default_timeout_seconds: int = 1800
    default_scan_profile: str = "safe-active"
    allow_public_targets: bool = False
    require_scope_file: bool = True
    artifact_dir: Path = Field(default=Path("appsec_runs"))


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    return settings
