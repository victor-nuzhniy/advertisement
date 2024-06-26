"""Project db settings."""

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from settings import Settings

postgres_indexes_naming_convention = {
    'ix': '%(column_0_label)s_idx',
    'uq': '%(table_name)s_%(column_0_name)s_key',
    'ck': '%(table_name)s_%(constraint_name)s_check',
    'fk': '%(table_name)s_%(column_0_name)s_fkey',
    'pk': '%(table_name)s_pkey',
}

Base = declarative_base(
    metadata=MetaData(naming_convention=postgres_indexes_naming_convention),
)

async_engine = create_async_engine(
    url=Settings.POSTGRES_DSN_ASYNC,
    echo=Settings.POSTGRES_ECHO,
)
engine = create_engine(url=Settings.POSTGRES_DSN, echo=Settings.POSTGRES_ECHO)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
