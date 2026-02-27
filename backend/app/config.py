
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_debug: bool = False
    app_title: str = "OpenFirst API"
    app_version: str = "0.1.0"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/openfirst"

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    github_pat: str = ""
    github_api_base: str = "https://api.github.com"
    github_max_retries: int = 3
    github_retry_delay: float = 1.0

    sync_interval_hours: int = 6
    full_sync_interval_hours: int = 24

    cache_ttl_repo_list: int = 900
    cache_ttl_repo_detail: int = 900
    cache_ttl_issues: int = 900
    cache_ttl_history: int = 3600
    cache_ttl_languages: int = 86400
    cache_ttl_stats: int = 3600


settings = Settings()
