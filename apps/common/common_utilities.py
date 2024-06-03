"""Common project utilities."""

from datetime import datetime
from typing import Callable

from fastapi import HTTPException, status
from jose import jwt
from pytz import utc
from sqlalchemy import DATETIME, Dialect, TypeDecorator
from typing_extensions import Any, Sequence, Type

from apps.authorization.schemas import TokenPayload
from apps.common.exceptions import BackendError
from settings import Settings

TIME = Type[datetime]


class AwareDateTime(TypeDecorator):
    """Results returned as aware datetimes, not naive ones."""

    impl = DATETIME
    cache_ok = True

    @property
    def python_type(
        self,
    ) -> Type[datetime]:
        """Get python type."""
        return datetime

    def process_bind_param(self, dt_value: Any | None, dialect: Dialect) -> Any | None:
        """Process bind parameter."""
        if dt_value is not None:
            if not dt_value.tzinfo:
                raise TypeError('tzinfo is required')
            dt_value = dt_value.astimezone(utc).replace(tzinfo=None)
        return dt_value

    def process_literal_param(self, dt_value: Any, dialect: Dialect) -> str:
        """Process literal parameter."""
        return str(dt_value)

    def process_result_value(self, dt_value: Any, dialect: Dialect) -> Any:
        """Process result value."""
        return dt_value.replace(tzinfo=utc)


def change_docstring(doc: str) -> Callable:
    """Change decorated function docstring."""

    def decorated_func(func: Callable) -> Callable:  # noqa
        """Change decorated function docstring."""
        func.__doc__ = doc
        return func

    return decorated_func


def get_token_data(token: str, access: bool = True) -> TokenPayload:
    """Get token data, using token."""
    key = Settings.JWT_SECRET_KEY if access else Settings.JWT_REFRESH_SECRET_KEY
    payload = jwt.decode(
        token,
        key,
        algorithms=[Settings.JWT_ALGORITHM],
    )
    token_data = TokenPayload(**payload)
    if datetime.fromtimestamp(token_data.exp) < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token data has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return token_data


class Checkers:
    """Different cases checkers."""

    def check_created_instance(
        self,
        instance: Any,
        name: str,
    ) -> Any:
        """Check whether inst is None and of Sequence type, return otherwise."""
        if instance is None:
            raise BackendError(message="{name} haven't been created".format(name=name))
        if isinstance(instance, Sequence):
            raise BackendError(
                message='Improper executor call',
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return instance


checkers = Checkers()
