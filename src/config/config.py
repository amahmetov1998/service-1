import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT
    date_format: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class RunConfig(BaseModel):
    host: str
    port: int
    reload: bool
    factory: bool = True


class RetryBudgetConfig(BaseModel):
    retry_cost: int
    retry_budget_ratio: float
    max_retry_budget: int
    max_retry_delay_seconds: int


class RedisConfig(BaseModel):
    url: RedisDsn
    cache_ttl_seconds: int
    socket_connect_timeout: float
    socket_timeout: float


class HTTPClientConfig(BaseModel):
    base_url: str
    timeout: int


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool
    echo_pool: bool
    max_overflow: int
    pool_size: int
    pool_pre_ping: bool = True


class WorkerConfig(BaseModel):
    pending_users_per_worker: int
    stuck_users_per_worker: int
    max_concurrent_tasks: int
    max_retry_count_per_user: int
    max_backoff_minutes: int
    poll_interval: int
    processing_timeout_seconds: int
    max_retry_count_per_user: int
    max_backoff_minutes: int


class BrokerProducerConfig(BaseModel):
    url: str
    acks: str
    enable_idempotence: bool
    notification_topic_name: str
    linger_ms: int  # сколько подождать, чтобы собрать несколько сообщений перед отправкой в брокер
    max_batch_size: int
    poll_interval: int
    max_retry_count_per_entity: int
    pending_tasks_per_publisher: int
    stuck_tasks_per_publisher: int
    processing_timeout_sec: int
    max_backoff_minutes: int


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    logging: LoggingConfig = LoggingConfig()
    run: RunConfig
    retry: RetryBudgetConfig
    client: HTTPClientConfig
    redis: RedisConfig
    db: DatabaseConfig
    worker: WorkerConfig
    broker: BrokerProducerConfig


settings = Settings()
