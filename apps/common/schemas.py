"""Common app schemas."""

from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Generic, Optional, Sequence, TypeVar, Union

from apps.common.enum import JSENDStatus

SchemaVar = TypeVar('SchemaVar', bound=Union[BaseModel, None, str])


class BaseInSchema(BaseModel):
    """Base schema for input."""

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class BaseOutSchema(BaseInSchema):
    """Base schema for output."""


class JSENDOutSchema(BaseModel, Generic[SchemaVar]):
    """Output JSEND schema with success status."""

    status: JSENDStatus = Field(default=JSENDStatus.SUCCESS)
    data: SchemaVar | Sequence[SchemaVar | None] | None  # noqa: WPS110
    message: Annotated[str, Field(examples=['Some message'])]
    code: int = Field(default=http_status.HTTP_200_OK)


class JSENDFailOutSchema(JSENDOutSchema):
    """Output JSEND schema with fail status."""

    status: JSENDStatus = Field(default=JSENDStatus.FAIL)
    data: Optional[str]  # noqa: WPS110
    code: int = Field(default=http_status.HTTP_400_BAD_REQUEST)


class JSENDErrorOutSchema(JSENDOutSchema):
    """Output JSEND schema with error status."""

    status: JSENDStatus = Field(default=JSENDStatus.ERROR)
    data: Optional[str]  # noqa: WPS110
    code: int = Field(default=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
