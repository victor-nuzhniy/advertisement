"""Authorization apps utilities functionality."""

from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pytz import utc
from typing_extensions import Any, Optional

from apps.common.common_types import ModelType
from apps.common.exceptions import BackendError
from settings import Settings

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    """Get hashed password."""
    return password_context.hash(password)


def create_access_token(subject: Any, expires_delta: int = 0) -> str:
    """Create user access token."""
    if expires_delta:
        expires_at = datetime.now(utc) + timedelta(seconds=expires_delta)
    else:
        expires_at = datetime.now(utc) + timedelta(
            seconds=Settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )
    to_encode = {'exp': expires_at, 'sub': str(subject)}
    return jwt.encode(to_encode, Settings.JWT_SECRET_KEY, Settings.JWT_ALGORITHM)


def create_refresh_token(subject: Any, expires_delta: int = 0) -> str:
    """Create user refresh token."""
    if expires_delta:
        expires_at = datetime.now(utc) + timedelta(seconds=expires_delta)
    else:
        expires_at = datetime.now(utc) + timedelta(
            seconds=Settings.JWT_REFRESH_TOKEN_EXPIRE_SECONDS,
        )
    to_encode = {'exp': expires_at, 'sub': str(subject)}
    return jwt.encode(
        to_encode,
        Settings.JWT_REFRESH_SECRET_KEY,
        Settings.JWT_ALGORITHM,
    )


def verify_user(user: Optional[ModelType]) -> None:
    """Check whether user is not none, and if it is - raise error."""
    if not user:
        raise BackendError(
            message='Login or password is invalid. Please, try again.',
        )


def verify_password(user: ModelType, password: str) -> None:
    """Verify user password."""
    if not check_password(password, user.password):
        raise BackendError(
            message='Login or password is invalid. Please, try again.',
        )


def check_password(password: str, hashed_pass: str) -> bool:
    """Check user password with password context."""
    return password_context.verify(password, hashed_pass)
