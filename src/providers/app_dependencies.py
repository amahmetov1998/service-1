from src.config import create_session_factory, AppDependencies, create_engine, settings
from .cache import create_redis
from .client import create_http_client
from .retry_strategy import create_retry_strategy


def create_app_dependencies() -> AppDependencies:

    http_client = create_http_client()
    redis = create_redis()
    retry_strategy = create_retry_strategy()
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)

    return AppDependencies(
        engine=engine,
        session_factory=session_factory,
        http_client=http_client,
        redis=redis,
        retry_strategy=retry_strategy,
    )
