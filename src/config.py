from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn, RedisDsn


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    factory: bool = True


class RetryBudgetConfig(BaseModel):
    retry_budget_ratio: float = 0.1
    tokens_for_retry: int = 100
    max_retries_global: int = 1
    max_retries_local: int = 3
    max_delay: int = 60


class RedisConfig(BaseModel):
    url: RedisDsn
    cache_ttl_seconds: int = 3600


class HTTPClientConfig(BaseModel):
    base_url: str = "http://localhost:8080"
    timeout: int = 10


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 5
    pool_size: int = 10
    pool_pre_ping: bool = True


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    retry: RetryBudgetConfig = RetryBudgetConfig()
    client: HTTPClientConfig = HTTPClientConfig()
    redis: RedisConfig
    db: DatabaseConfig


settings = Settings()
