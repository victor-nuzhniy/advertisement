"""Pytest fixtures for tests package."""

from typing import Generator

import psycopg2
import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.engine import URL

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
