"""Test models."""

from apps.user.models import User
from tests.apps.user.factories import UserFactory
from tests.bases import BaseModelFactory


class TestUser:
    """Class for testing User model."""

    def test_factory(self) -> None:
        """Test model factory."""
        BaseModelFactory.check_factory(factory_class=UserFactory, model=User)

    def test_repr(self) -> None:
        """Test __repr__ method."""
        user_object: User = UserFactory()
        expected_result: str = ''.join(
            (
                '{name}(id={id}, username={username}, email={email}, '.format(
                    name=user_object.__class__.__name__,
                    id=user_object.id,
                    username=user_object.username,
                    email=user_object.email,
                ),
                'is_active={is_active}, is_admin={is_admin}, '.format(
                    is_active=user_object.is_active,
                    is_admin=user_object.is_admin,
                ),
                'created_at={created_at})'.format(
                    created_at=user_object.created_at,
                ),
            ),
        )
        actual_result = user_object.__repr__()  # noqa
        assert expected_result == actual_result
