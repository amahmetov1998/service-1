from src.config import WorkDependencies, create_session_factory, create_engine, settings
from .client import create_http_client
from .retry_strategy import create_retry_strategy


def create_work_dependencies() -> WorkDependencies:

    http_client = create_http_client()
    retry_strategy = create_retry_strategy()
    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)

    return WorkDependencies(
        engine=engine,
        session_factory=session_factory,
        http_client=http_client,
        retry_strategy=retry_strategy,
    )
