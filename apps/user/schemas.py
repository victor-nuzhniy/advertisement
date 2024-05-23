"""User apps schemas."""

from re import fullmatch

from pydantic import (
    Field,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

from apps.authorization.auth_utilities import get_hashed_password
from apps.authorization.schemas import UserOut
from apps.common.constants import EMAIL_REGEX
from apps.common.schemas import BaseInSchema, BaseOutSchema


class CreateUserIn(BaseInSchema):
    """User creation in schema."""

    username: Annotated[
        str,
        Field(min_length=1, max_length=50, examples=['Alex'], description='User name'),
    ]
    email: Annotated[
        str,
        Field(max_length=100, examples=['a@a.com'], description='User email'),
    ]
    password_check: Annotated[
        str,
        Field(
            exclude=True,
            validation_alias='password',
            min_length=1,
            max_length=120,
            examples=['111'],
            description='User password',
        ),
    ]
    password_re_check: Annotated[
        str,
        Field(exclude=True, examples=['111'], description='User password recheck'),
    ]

    @computed_field
    def password(self) -> str:
        """Hash password."""
        return get_hashed_password(self.password_check)

    @field_validator('email')
    @classmethod
    def validate_email(cls, email_value: str) -> str:
        """Validate email field."""
        if not fullmatch(EMAIL_REGEX, email_value):
            raise ValueError('Invalid email address format')
        return email_value

    @model_validator(mode='after')
    def re_check_password(self) -> 'CreateUserIn':
        """Check whether password_re_check is equal to password."""
        password = self.password_check
        r_password = self.password_re_check
        if password is not None and r_password is not None and password != r_password:
            raise ValueError("Password don't match!")
        return self


class CreateUserOut(BaseOutSchema):
    """User creation out schema."""

    id: Annotated[int, Field(description='Created user id', examples=[1])]
    username: Annotated[str, Field(description='Created username', examples=['Alex'])]
    email: Annotated[str, Field(description='Created user email', examples=['a@a.com'])]
    is_active: Annotated[
        bool,
        Field(description='Created user "is_active" status', examples=[True]),
    ]


class AdminPartiallyUserIn(BaseInSchema):
    """User partially update in schema for admin interface."""

    username: str | None = None
    email: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, email_value: str) -> str:
        """Validate email field."""
        if email_value is not None:
            if not fullmatch(EMAIL_REGEX, email_value):
                raise ValueError('Invalid email address format')
            return email_value
        raise ValidationError('Email may not be empty')


class AdminUserIn(BaseInSchema):
    """User update in schema for admin interface."""

    username: Annotated[str, Field(description='Update username', examples=['Alex'])]
    email: Annotated[str, Field(description='Update user email', examples=['a@a.com'])]
    is_active: Annotated[
        bool,
        Field(description='Update user "is_active" status', examples=[True]),
    ]
    is_admin: Annotated[
        bool,
        Field(description='Update user "is_admin" status', examples=[True]),
    ]

    @field_validator('email')
    @classmethod
    def validate_email(cls, email_value: str) -> str:
        """Validate email field."""
        if not fullmatch(EMAIL_REGEX, email_value):
            raise ValueError('Invalid email address format')
        return email_value


class CreateAdminUserIn(CreateUserIn):
    """User create in schema for admin interface."""

    is_active: Annotated[
        bool,
        Field(description='Created user "is_active" status', examples=[True]),
    ]
    is_admin: Annotated[
        bool,
        Field(description='Update user "is_admin" status', examples=[True]),
    ]


class AdminUserOut(UserOut):
    """User out schema for admin interface."""
