"""Bases for tests."""

import datetime
import random
from typing import Any, Sequence, Type

import factory
from pydantic_factories import AsyncPersistenceProtocol, ModelFactory, PostGenerated
from pytz import utc

from apps.common.base_statements import BaseCRUDStatements
from apps.common.common_types import ModelType, SchemaType
from apps.common.db import Base, async_session_factory
from apps.common.orm_services import statement_executor as executor

starting_seq_num = 0


class AsyncPersistenceHandler(AsyncPersistenceProtocol):
    """AsyncPersistenceHandler class."""

    def __init__(self, model: Type[Base]) -> None:
        """Initialize class."""
        self._model = model
        self._service = BaseCRUDStatements(model=self._model)

    async def save(
        self,
        model_data: SchemaType,  # type: ignore
    ) -> ModelType | Sequence[ModelType] | None:
        """Save given model_data."""
        async with async_session_factory() as db_session:
            async with db_session.begin():
                statement = self._service.create_statement(schema=model_data)
                return await executor.execute_return_statement(
                    session=db_session,
                    statement=statement,
                    commit=True,
                )

    async def save_many(
        self,
        model_data: SchemaType,  # type: ignore
    ) -> list[ModelType] | Sequence[list[ModelType]] | None:
        """Save many given model_data."""
        async with async_session_factory() as db_session:
            async with db_session.begin():
                statement = self._service.create_many_statement(schemas=model_data)
                return await executor.execute_return_statement(
                    session=db_session,
                    statement=statement,
                    commit=True,
                    many=True,
                )


class BaseRawFactory(ModelFactory):
    """Base raw factory class."""

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """Mock field type."""
        type_name = str(field_type.__name__)
        if type_name == 'Email':
            return cls.get_faker().email()
        return super().get_mock_value(field_type)


def generate_dt(name: str, values_data: dict[str, Any]) -> datetime.datetime:
    """Generate now datetime with tz."""
    return datetime.datetime.now(tz=utc)


class BaseFactory(BaseRawFactory):
    """BaseFactory class."""

    created_at: datetime.datetime = PostGenerated(fn=generate_dt)


class BaseModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base model factory class."""

    class Meta:
        """Class Meta for BaseModelFactory class."""

        abstract = True
        sqlalchemy_session_persistence = 'commit'

    def check_factory(
        self,
        factory_class: Type['BaseModelFactory'],
        model: Type[Base],
    ) -> None:
        """Test that factory creates successfully."""
        model_object = factory_class()
        size = random.randint(2, 3)  # noqa
        model_objects = factory_class.create_batch(size=size)

        assert isinstance(model_object, model)
        assert size == len(model_objects)
        for elem in model_objects:
            assert isinstance(elem, model)

    @classmethod
    def _create(cls, model_class: ModelType, *args: Any, **kwargs: Any) -> ModelType:
        """Change RuntimeError to help with factory set up."""
        if cls._meta.sqlalchemy_session is None:
            raise RuntimeError(
                ''.join(
                    (
                        'Register {name} factory inside '.format(name=cls.__name__),
                        'conftest.py in set_session_for_factories fixture declaration.',
                    ),
                ),
            )
        return super()._create(model_class, *args, **kwargs)
