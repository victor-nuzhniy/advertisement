"""Advertisement model factories."""

import factory
from pytz import utc

from apps.advertisements.models import Advertisement
from tests.bases import BaseModelFactory


class AdvertisementFactory(BaseModelFactory):
    """Advertisement model factory."""

    id = factory.Sequence(lambda idx: idx + 3000)
    url = factory.Faker('uri')
    name = factory.Faker('city')
    price = factory.Faker('pyint')
    model = factory.Faker('country')
    region = factory.Faker('city')
    run = factory.Faker('pyint')
    color = factory.Faker('color_name')
    salon = factory.Faker('pystr', max_chars=50)
    seller = factory.Faker('first_name')
    adv_date = factory.Faker('date')
    created_at = factory.Faker('date_time', tzinfo=utc)

    @classmethod
    def _setup_next_sequence(cls) -> int:
        """Set next sequence value."""
        return 1

    class Meta:
        """Class Meta for Advertisement factory class."""

        model = Advertisement
