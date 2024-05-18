"""Module for testing advertisement apps handlers."""

from faker import Faker
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.schemas import AdvPeriodQuerySchema
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
        expected_result: list = []
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
        for index, elem in enumerate(actual_result):  # type: ignore
            assert elem.id == expected_result[index].id
