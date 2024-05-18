"""Factories for user apps."""

import factory
from pytz import utc

from apps.authorization.auth_utilities import get_hashed_password
from apps.user.models import User
from tests.bases import BaseModelFactory, UniqueFaker


class UserFactory(BaseModelFactory):
    """User model factory."""

    id = factory.Sequence(lambda idx: idx + 3000)
    username = UniqueFaker('pystr', min_chars=1, max_chars=50)
    simple_password = factory.Faker('pystr', min_chars=1, max_chars=120)
    password = factory.LazyAttribute(
        function=lambda el: get_hashed_password(el.simple_password),
    )
    email = UniqueFaker('email')
    is_active = factory.Faker('pybool')
    is_admin = factory.Faker('pybool')
    created_at = factory.Faker('date_time', tzinfo=utc)

    @classmethod
    def _setup_next_sequence(cls) -> int:
        """Set next sequence value."""
        return 1

    class Meta:
        """Class Meta for User factory class."""

        model = User
        exclude = ('simple_password',)
