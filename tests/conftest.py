import asyncio
import os
import subprocess

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer
from testcontainers.core.container import DockerContainer

from src.api import healthcheck_router, user_phones_router
from src.application import create_app
from src.clients import ServicePhoneClient
from src.config import (
    RedisCache,
    RetryBudgetStrategy,
    create_engine,
    create_session_factory,
)
from src.dependencies import (
    get_redis,
    get_session_factory,
    get_retry_strategy,
    get_service_phone_client,
)
from src.handlers import register_errors_handlers


@pytest.fixture(scope="session")
def postgres_container():

    with PostgresContainer("postgres:16") as postgres:
        postgres_url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
        os.environ["DATABASE_URL"] = postgres_url
        yield postgres_url


os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture(scope="session")
def external_service_db():

    with PostgresContainer("postgres:16") as postgres:
        postgres_url = (
            postgres.get_connection_url()
            .replace("psycopg2", "asyncpg")
            .replace(
                "localhost",
                "host.docker.internal",
            )
        )
        yield postgres_url


@pytest.fixture(scope="session")
def apply_migrations(postgres_container):

    subprocess.run(
        [
            "alembic",
            "upgrade",
            "head",
        ],
        check=True,
    )


@pytest_asyncio.fixture(scope="session")
async def engine(apply_migrations, postgres_container):

    engine = create_engine(
        url=postgres_container,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def override_get_session_factory(engine):

    session_factory = create_session_factory(
        engine=engine,
    )

    yield session_factory


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer() as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        yield f"redis://{host}:{port}"


@pytest_asyncio.fixture(scope="session")
async def override_get_redis(redis_container):
    redis = RedisCache(
        redis_url=redis_container,
        cache_ttl_seconds=3600,
        socket_timeout=0.2,
        socket_connect_timeout=0.2,
    )
    yield redis

    await redis.close()


async def wait_service(service_url):
    for _ in range(10):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{service_url}/healthcheck")
                if response.status_code == 200:
                    return
        except Exception:
            pass

        await asyncio.sleep(1)


@pytest_asyncio.fixture(scope="session")
async def external_service(external_service_db):

    container = DockerContainer("service-2-app:latest")

    container.with_env(
        "APP_CONFIG__DB__URL",
        external_service_db,
    )
    container.with_exposed_ports(8080)
    with container as service:

        port = service.get_exposed_port(8080)
        service_url = f"http://localhost:{port}"

        await wait_service(service_url)

        yield service_url


@pytest_asyncio.fixture
async def http_client(external_service):

    client = httpx.AsyncClient(
        base_url=external_service,
    )

    yield client

    await client.aclose()


@pytest_asyncio.fixture
async def override_get_retry_strategy():
    retry_strategy = RetryBudgetStrategy(
        retry_cost=10,
        retry_budget_ratio=0.1,
        max_retry_budget=3,
    )
    yield retry_strategy


@pytest_asyncio.fixture
async def override_get_service_phone_client(http_client, override_get_retry_strategy):
    service_phone_client = ServicePhoneClient(
        client=http_client,
        retry_strategy=override_get_retry_strategy,
    )
    yield service_phone_client


@pytest.fixture
def app():
    app = create_app()
    register_errors_handlers(app)
    app.include_router(healthcheck_router)
    app.include_router(user_phones_router)
    return app


@pytest.fixture
def override_dependencies(
    app,
    override_get_redis,
    override_get_session_factory,
    override_get_retry_strategy,
    override_get_service_phone_client,
):
    app.dependency_overrides[get_redis] = lambda: override_get_redis
    app.dependency_overrides[get_session_factory] = lambda: override_get_session_factory
    app.dependency_overrides[get_retry_strategy] = lambda: override_get_retry_strategy
    app.dependency_overrides[get_service_phone_client] = (
        lambda: override_get_service_phone_client
    )

    yield

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_client(app, override_dependencies):
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client


@pytest_asyncio.fixture
async def unavailable_http_client():

    client = httpx.AsyncClient(
        base_url="http://localhost:9999",
        timeout=1,
    )

    yield client

    await client.aclose()


@pytest_asyncio.fixture
async def override_get_unavailable_service_phone_client(
    unavailable_http_client, override_get_retry_strategy
):
    service_phone_client = ServicePhoneClient(
        client=unavailable_http_client,
        retry_strategy=override_get_retry_strategy,
    )
    yield service_phone_client


@pytest.fixture
def override_unavailable_service(
    app,
    override_dependencies,
    override_get_unavailable_service_phone_client,
):
    app.dependency_overrides[get_service_phone_client] = (
        lambda: override_get_unavailable_service_phone_client
    )

    yield


@pytest_asyncio.fixture
async def client_with_unavailable_service(app, override_unavailable_service):
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client


@pytest.fixture
def user_payload():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "test@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234567",
                "phone_type": "mobile",
                "is_verified": False,
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }


@pytest.fixture
def user_with_duplicate_email():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "test@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234567",
                "phone_type": "mobile",
                "is_verified": False,
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }


@pytest.fixture
def user_with_duplicate_phone():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "test2@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234567",
                "phone_type": "mobile",
                "is_verified": "false",
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }


@pytest.fixture
def cached_user():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "cache@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234568",
                "phone_type": "mobile",
                "is_verified": False,
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }


@pytest.fixture
def user_unavailable_service():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "fail@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234561",
                "phone_type": "mobile",
                "is_verified": "false",
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }


@pytest.fixture
def user_service_payload():
    return {
        "first_name": "Test",
        "last_name": "Test",
        "email": "test_service@example.com",
        "phone_numbers": [
            {
                "phone_number": "+79991234569",
                "phone_type": "mobile",
                "is_verified": False,
                "operator_type": "mts",
                "region_type": "moscow_city",
                "is_spam": False,
            }
        ],
    }
