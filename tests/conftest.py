"""Pytest fixtures for tests package."""

import asyncio
import random
from typing import Any, AsyncGenerator, Generator, Type

import fastapi
import httpx
import psycopg2
import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pytest_alembic import Config, runner
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from apps.common.db import async_session_factory as AsyncSessionFactory  # noqa
from apps.common.db import session_factory as SessionFactory  # noqa
from apps.common.dependencies import get_async_session, get_session
from settings import Settings
from tests.apps.user.factories import UserFactory
from tests.bases import BaseModelFactory


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
def custom_event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
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
    custom_event_loop: asyncio.AbstractEventLoop,
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
    custom_event_loop: asyncio.AbstractEventLoop,
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


@pytest.fixture(scope='session')
def alembic_config() -> Config:
    """Get alembic configuration fixture."""
    return Config()


@pytest.fixture(scope='session')
def alembic_engine(sync_db_engine: Engine) -> Engine:
    """Get alembic sync engine fixture."""
    return sync_db_engine


@pytest.fixture(scope='session')
def alembic_runner(
    alembic_config: Config,
    alembic_engine: Engine,
) -> Generator[runner, None, None]:
    """Get alembic runner fixture."""
    config = Config.from_raw_config(alembic_config)
    with runner(config=config, engine=alembic_engine) as alembic_runner:
        yield alembic_runner


@pytest.fixture(scope='session', autouse=True)
def apply_migrations(
    create_database: None,
    alembic_runner: runner,
    alembic_engine: Engine,
) -> Generator[None, None, None]:
    """Apply all migrations from base to head."""
    alembic_runner.migrate_up_to(revision='head')
    yield
    alembic_runner.migrate_down_to(revision='base')


@pytest.fixture(scope='session')
def sync_db_engine() -> Generator[Engine, None, None]:
    """Create sync database engine and dispose it after all tests.

    Yields:
        engine (Engine): SQLAlchemy Engine instance.
    """
    engine = create_engine(url=Settings.POSTGRES_DSN, echo=Settings.POSTGRES_ECHO)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope='session')
async def async_db_engine(
    custom_event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[AsyncEngine, None]:
    """Create async database engine and dispose it after all tests.

    Yields:
        async_engine (AsyncEngine): SQLAlchemy AsyncEngine instance.
    """
    async_engine = create_async_engine(
        url=Settings.POSTGRES_DSN_ASYNC,
        echo=Settings.POSTGRES_ECHO,
    )
    try:
        yield async_engine
    finally:
        await async_engine.dispose()


@pytest.fixture(scope='function')
def sync_session_factory(sync_db_engine: Engine) -> Generator[sessionmaker, None, None]:
    """Create async session factory."""
    yield sessionmaker(bind=sync_db_engine, expire_on_commit=False, class_=Session)


@pytest.fixture(scope='function')
async def session_factory(
    async_db_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker, None]:
    """Create async session factory."""
    yield async_sessionmaker(
        bind=async_db_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(scope='function')
def sync_db_session(
    sync_session_factory: sessionmaker,
) -> Generator[Session, None, None]:
    """Create sync session for database and rollback it after test."""
    with sync_session_factory() as session:
        yield session
        session.rollback()
        session.close()


@pytest.fixture(scope='function')
async def db_session(
    session_factory: sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for database and rollback it after test."""
    async with session_factory(autoflush=False) as async_session:
        yield async_session
        await async_session.rollback()
        await async_session.close()


@pytest.fixture(scope='session')
def scoped_db_session() -> Generator[scoped_session, None, None]:
    """Create scoped session for tests runner and model factories."""
    session = scoped_session(session_factory=SessionFactory)
    yield session
    session.rollback()
    session.close()


@pytest.fixture(autouse=True, scope='session')
def set_session_for_factories(scoped_db_session: scoped_session) -> None:
    """
    Registration of model factories.

    To set up a scoped session during the test run.
    """
    known_factories: list[Type[BaseModelFactory]] = [
        UserFactory,
        # === Add new factory classes here!!! ===
    ]

    for factory_class in known_factories:
        # Set up session to factory
        factory_class._meta.sqlalchemy_session = scoped_db_session
