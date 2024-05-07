"""Common project types."""

from __future__ import annotations

from pydantic import BaseModel
from typing_extensions import TypeVar

from apps.common.db import Base

ModelType = TypeVar('ModelType', bound=Base)
SchemaType = TypeVar('SchemaType', bound=BaseModel, covariant=True)
