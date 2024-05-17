"""Pytest fixtures for tests package."""

import pytest
from _pytest.monkeypatch import MonkeyPatch  # noqa
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
