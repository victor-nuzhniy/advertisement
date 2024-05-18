"""Test adv_utilities module functionality."""

from faker import Faker

from apps.advertisements.adv_utilities import adv_auxiliary_func
from tests.apps.advertisements.factories import AdvertisementFactory


class TestAdvAuxGetStatisticalInfo:
    """Test get_statistical_info method of AdvAuxiliaryFunc class."""

    def test_get_statistical_info(
        self,
        faker: Faker,
    ) -> None:
        """Test get_statistical_info method."""
        number = faker.random_int(min=3, max=7)
        input_list: list = []
        for index in range(1, number + 1):
            input_list.extend(
                [
                    AdvertisementFactory(
                        price=index,
                        adv_date=faker.date_between(start_date='-1d'),
                    ),
                    AdvertisementFactory(
                        price=index,
                        adv_date=faker.date_between(start_date='-7d', end_date='-1d'),
                    ),
                    AdvertisementFactory(
                        price=index,
                        adv_date=faker.date_between(start_date='-30d', end_date='-7d'),
                    ),
                ],
            )
        actual_result = adv_auxiliary_func.get_statistical_info(input_list)
        assert actual_result.min_price == 1
        assert actual_result.max_price == number
        assert actual_result.num_day == number
        assert actual_result.num_week == 2 * number
        assert actual_result.num_month == 3 * number
