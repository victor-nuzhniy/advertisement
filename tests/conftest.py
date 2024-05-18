"""Pytest fixtures for tests package."""

import asyncio
import random
from typing import Any, AsyncGenerator, Generator

import fastapi
import httpx
import psycopg2
import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine import URL, Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session

from apps.common.db import async_session_factory as AsyncSessionFactory  # noqa
from apps.common.db import session_factory as SessionFactory  # noqa
from apps.common.dependencies import get_async_session, get_session
from settings import Settings


@pytest.fixture(scope='session', autouse=True)
def mock_db_url(monkeypatch_session: MonkeyPatch) -> None:
    """Change all PostgreSQL URLs and environments to use `test` database."""
    db_url: URL | str = Settings.POSTGRES_DSN
    async_db_url: URL | str = Settings.POSTGRES_DSN_ASYNC
    if isinstance(db_url, str) or isinstance(async_db_url, str):
        raise ValueError(
            ''.join(
                (
                    "POSTGRES_DSN and POSTGRES_DSN_ASYNC shouldn't be set in .env",
                    "file for testing. 'test' will be used as testing database name.",
                ),
            ),
        )
    monkeypatch_session.setattr(
        target=Settings,
        name='POSTGRES_DSN',
        value=db_url.set(database='test'),
    )
    monkeypatch_session.setattr(
        target=Settings,
        name='POSTGRES_DSN_ASYNC',
        value=async_db_url.set(database='test'),
    )
    monkeypatch_session.setenv(name='POSTGRES_DB', value='test')
    monkeypatch_session.setattr(target=Settings, name='POSTGRES_DB', value='test')


@pytest.fixture(scope='session', autouse=True)
def create_database(mock_db_url: None) -> Generator[None, None, None]:  # noqa
    """Recreate 'test' database for tests."""
    con = psycopg2.connect(
        'postgresql://{user}:{password}@{host}:{port}'.format(
            user=Settings.POSTGRES_USER,
            password=Settings.POSTGRES_PASSWORD,
            host=Settings.POSTGRES_HOST,
            port=Settings.POSTGRES_PORT,
        ),
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS {db};'.format(db=Settings.POSTGRES_DB))
    cursor.execute('CREATE DATABASE {db};'.format(db=Settings.POSTGRES_DB))
    yield
    cursor.execute('DROP DATABASE IF EXISTS {db};'.format(db=Settings.POSTGRES_DB))


@pytest.fixture(scope='session')
def monkeypatch_session() -> MonkeyPatch:
    """Create monkeypatch for session scope.

    Yields:
        monkeypatch (MonkeyPatch): MonkeyPatch instance with `session`
        (one time per tests run)
    """
    monkeypatch = MonkeyPatch()
    yield monkeypatch
    monkeypatch.undo()


@pytest.fixture(scope='session', autouse=True)
def no_http_requests(monkeypatch_session: MonkeyPatch) -> None:  # noqa
    """Disable HTTP requests for 3-rd party libraries.

    Notes:
        This isn't working with 'httpx', because it uses in tests to call
         Back-end API endpoints.
    """

    def raise_mock(*args: Any, **kwargs: Any) -> None:  # noqa
        """Thrown and exception when tests try to use HTTP connection.

        Raises:
            RuntimeError: indicates that HTTPS request found.
        """
        raise RuntimeError(
            'Found request: {args}, {kwargs}'.format(args=args, kwargs=kwargs),
        )

    # Disable library `urllib3`
    monkeypatch_session.setattr(
        target='urllib3.connectionpool.HTTPConnectionPool.urlopen',
        name=raise_mock,
    )
    # Disable library `urllib`
    monkeypatch_session.setattr(target='urllib.request.urlopen', name=raise_mock)
    # Disable BackgroundTasks
    monkeypatch_session.setattr(
        target='fastapi.BackgroundTasks.add_task',
        name=raise_mock,
    )
    # Disable library `requests`
    monkeypatch_session.setattr(
        target='requests.sessions.Session.request',
        name=raise_mock,
    )


@pytest.fixture(scope='session', autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create asyncio (uvloop) for tests runtime.

    Yields:
        loop (asyncio.AbstractEventLoop): Shared with FastAPI, asyncio instance
         loop, that created for tests runs.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def mock_session_factories(
    async_db_engine: AsyncEngine,
    sync_db_engine: Engine,
) -> AsyncGenerator[None, None]:
    """Mock session_factory and async_factory from `apps.common.db`.

    Notes:
        This should prevent errors with middlewares, that are using these methods.
    """
    AsyncSessionFactory.configure(bind=async_db_engine)
    SessionFactory.configure(bind=sync_db_engine)
    yield


@pytest.fixture(scope='function')
async def app_fixture(
    db_session: AsyncSession,
    sync_db_session: Session,
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[fastapi.FastAPI, None]:
    """Override dependencies for FastAPI and returns FastAPI instance (app).

    Yields:
        app (fastapi.FastAPI): Instance of FastAPI ASGI application.
    """

    async def override_get_async_session() -> AsyncSession:
        """
        Replace get_async_session dependency with AsyncSession.

        From `db_session` fixture.
        """
        return db_session

    def override_get_session() -> Session:
        """
        Replace get_session dependency with Session.

        From `sync_db_session` fixture.
        """
        return sync_db_session

    from apps.main import app

    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[get_session] = override_get_session
    yield app


@pytest.fixture(scope='function')
async def async_client(
    app_fixture: fastapi.FastAPI,
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Prepare async HTTP client with FastAPI app context.

    Yields:
        httpx_client (httpx.AsyncClient): Instance of AsyncClient to
        perform a requests to API.
    """
    async with httpx.AsyncClient(
        app=app_fixture,
        base_url='http://{host}:{port}'.format(host=Settings.HOST, port=Settings.PORT),
    ) as httpx_client:
        yield httpx_client


@pytest.fixture(scope='function', autouse=True)
def faker_seed() -> None:
    """Generate random seed for Faker instance."""
    return random.seed(version=3)
