"""Authorization schemas."""

from datetime import datetime

from pydantic import Field
from typing_extensions import Annotated

from apps.common.schemas import BaseInSchema, BaseOutSchema


class TokenPayload(BaseInSchema):
    """Token payload schema."""

    exp: Annotated[int, Field(description='Expired at')]
    sub: Annotated[str, Field(description='Subject')]


class UserOut(BaseOutSchema):
    """User out schema."""

    id: Annotated[int, Field(description='Current user id', examples=[1])]
    username: Annotated[
        str,
        Field(description='Current user username', examples=['Alex']),
    ]
    email: Annotated[str, Field(description='Current user email', examples=['a@a.com'])]
    is_active: Annotated[
        bool,
        Field(description='Current user "is_active" status', examples=['True']),
    ]
    is_admin: Annotated[
        bool,
        Field(description='Current user "is_admin" status', examples=['True']),
    ]
    last_visit_at: Annotated[
        datetime,
        Field(description='Current user last visit date'),
    ]
    created_at: Annotated[datetime, Field(description='Current user creation date')]
    updated_at: Annotated[
        datetime,
        Field(description='Current user last updation date'),
    ]


class UserIn(TokenPayload):
    """User in schema."""

    id: Annotated[int, Field(description='User id', examples=[1])]


class AuthOut(BaseOutSchema):
    """Authorization out schema."""

    access_token: Annotated[str, Field(description='User access token')]
    refresh_token: Annotated[str, Field(description='User refresh token')]
    id: Annotated[int, Field(description='User id')]
