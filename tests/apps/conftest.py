"""Apps test module fixtures."""

import pytest
from faker import Faker

from apps.authorization.auth_utilities import create_access_token
from apps.user.models import User
from tests.apps.user.factories import UserFactory


@pytest.fixture(scope='function')
async def access_token(
    faker: Faker,
) -> str:
    """Get access validation token."""
    user: User = UserFactory(email=faker.email())
    return create_access_token(subject=user.email)
