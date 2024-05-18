"""Bases for tests."""

import random
from typing import Any, Type

import factory
from faker import Faker

from apps.common.common_types import ModelType
from apps.common.db import Base

starting_seq_num = 0


class BaseModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base model factory class."""

    class Meta:
        """Class Meta for BaseModelFactory class."""

        abstract = True
        sqlalchemy_session_persistence = 'commit'

    @staticmethod
    def check_factory(  # noqa
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


class UniqueFaker(factory.Faker):
    """UniqueFaker class."""

    def evaluate(self, instance, step, extra):  # type: ignore
        """Evaluate faker instance."""
        locale = extra.pop('locale')
        subfaker: Faker = self._get_faker(locale)
        unique_proxy = subfaker.unique
        return unique_proxy.format(self.provider, **extra)
