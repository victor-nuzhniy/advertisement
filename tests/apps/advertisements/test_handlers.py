"""Module for testing advertisement apps handlers."""

from typing import Sequence, Sized

import factory
from faker import Faker
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import (
    AdvInList,
    AdvNameModelQuerySchema,
    AdvPeriodQuerySchema,
    CreateAdvIn,
)
from tests.apps.advertisements.factories import AdvertisementFactory


class TestAdvHandlersGetAdvPeriodList:
    """Test get_adv_period_list of AdvHandlers class."""

    async def test_get_adv_period_list(
        self,
        faker: Faker,
        db_session: AsyncSession,
    ) -> None:
        """Test get_adv_period_list method."""
        number = faker.random_int(min=3, max=5)
        start_date = faker.date_between(start_date='-50d', end_date='-30d')
        end_date = faker.date_between(start_date='-20d', end_date='-10d')
        period = AdvPeriodQuerySchema(
            begin=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
        )
        already_in_db = await adv_handlers.get_adv_period_list(
            Request({'type': 'http'}),
            db_session,
            period,
        )
        expected_result: list[Advertisement] = []
        for _ in range(1, number + 1):
            expected_result.append(
                AdvertisementFactory(
                    adv_date=faker.date_between(start_date='-29d', end_date='-21d'),
                ),
            )
            AdvertisementFactory(
                adv_date=faker.date_between(start_date='-60d', end_date='-51d'),
            )
            AdvertisementFactory(adv_date=faker.date_between(start_date='-9d'))
        actual_result = await adv_handlers.get_adv_period_list(
            Request({'type': 'http'}),
            db_session,
            period,
        )
        assert isinstance(actual_result, Sequence)
        assert isinstance(already_in_db, Sized)
        for index, elem in enumerate(expected_result):
            assert (
                elem.id == actual_result[index + len(already_in_db)].id  # type: ignore
            )


class TestGetNameModelStat:
    """Class for testing get_name_model_stat handler."""

    async def test_get_name_model_stat(
        self,
        faker: Faker,
        db_session: AsyncSession,
    ) -> None:
        """Test get_name_model_stat method."""
        name = faker.pystr(min_chars=10)
        model = faker.pystr(min_chars=11)
        number = faker.random_int(min=3, max=7)
        for index in range(1, number + 1):
            AdvertisementFactory(
                name=name,
                model=model,
                price=index,
                adv_date=faker.date_between(start_date='-1d'),
            )
            AdvertisementFactory(
                name=name,
                model=model,
                price=index,
                adv_date=faker.date_between(start_date='-7d', end_date='-1d'),
            )
            AdvertisementFactory(
                name=name,
                model=model,
                price=index,
                adv_date=faker.date_between(start_date='-30d', end_date='-7d'),
            )
            AdvertisementFactory.create_batch(3)
        actual_result = await adv_handlers.get_name_model_stat(
            Request({'type': 'http'}),
            db_session,
            AdvNameModelQuerySchema(name=name, model=model),
        )
        assert actual_result['min_price'] == 1
        assert actual_result['max_price'] == number
        assert actual_result['num_day'] == number
        assert actual_result['num_week'] == 2 * number
        assert actual_result['num_month'] == 3 * number


class TestBulkCreateAdv:
    """Class for testing bulk_create_adv handler."""

    async def test_bulk_create_adv(
        self,
        faker: Faker,
        db_session: AsyncSession,
    ) -> None:
        """Test bulk_create_adv handler."""
        number: int = faker.random_int(min=3, max=5)
        expected_result: list[CreateAdvIn | None] = []
        for _ in range(number):
            model_dict = factory.build(dict, FACTORY_CLASS=AdvertisementFactory)
            model_dict.pop('created_at')
            expected_result.append(CreateAdvIn(**model_dict))
        await adv_handlers.bulk_create_adv(
            Request({'type': 'http'}),
            db_session,
            AdvInList(item_list=expected_result),
        )
        saved_advs = await adv_handlers.get_adv_period_list(
            Request({'type': 'http'}),
            db_session,
            AdvPeriodQuerySchema(),
        )
        assert isinstance(saved_advs, Sequence)
        for index, elem in enumerate(saved_advs[-number:]):
            for attr in ('name', 'price', 'url', 'model', 'adv_date'):
                assert getattr(expected_result[index], attr) == getattr(elem, attr)
