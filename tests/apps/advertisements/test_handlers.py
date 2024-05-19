"""Module for testing advertisement apps handlers."""

from typing import Sequence, Sized

from faker import Faker
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import AdvNameModelQuerySchema, AdvPeriodQuerySchema
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
