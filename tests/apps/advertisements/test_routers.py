"""Module for testing advertisement apps."""

from typing import Sequence

from faker import Faker
from fastapi import FastAPI, Request, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import AdvPeriodQuerySchema
from apps.common.enum import JSENDStatus
from tests.apps.advertisements.factories import AdvertisementFactory


class TestGetAdvertisementByPeriod:
    """Class for testing get_advertisement_by_period router."""

    async def test_get_advertisement_by_period(
        self,
        faker: Faker,
        async_client: AsyncClient,
        app_fixture: FastAPI,
        db_session: AsyncSession,
        access_token: str,
    ) -> None:
        """Test get_advertisement_by_period router."""
        number = faker.random_int(min=3, max=5)
        start_date = faker.date_between(start_date='-50d', end_date='-30d')
        end_date = faker.date_between(start_date='-20d', end_date='-10d')
        period = AdvPeriodQuerySchema(
            begin=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
        )
        gap: int = len(
            await adv_handlers.get_adv_period_list(  # type: ignore
                Request({'type': 'http'}),
                db_session,
                period,
            ),
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
        actual_result = await async_client.get(
            url=app_fixture.url_path_for('adv_period'),
            params={'begin': period.begin, 'end': period.end},
            headers={'Authorization': 'Bearer {token}'.format(token=access_token)},
        )
        response_json = actual_result.json()
        actual_data = response_json['data']
        assert actual_result.status_code == status.HTTP_200_OK
        assert response_json['status'] == JSENDStatus.SUCCESS
        assert response_json['message'] == ''.join(
            (
                'Get advertisements list with begin - {begin}'.format(
                    begin=period.begin,
                ),
                ' and end - {end} period'.format(end=period.end),
            ),
        )
        assert response_json['code'] == status.HTTP_200_OK
        assert isinstance(actual_data, Sequence)
        for index, elem in enumerate(expected_result):
            for key, key_val in actual_data[index + gap].items():
                if key == 'adv_date':
                    assert getattr(elem, key).strftime('%Y-%m-%d') == key_val
                elif key == 'created_at':
                    assert (
                        getattr(elem, key).strftime('%Y-%m-%dT%H:%M:%S.%fZ') == key_val
                    )
                else:
                    assert getattr(elem, key) == key_val
