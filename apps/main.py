"""Main FastAPI module."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.advertisements.routers import adv_router
from apps.common.exceptions import BackendError
from apps.common.exceptions_handlers import (
    backend_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from apps.user.routers import users_router
from settings import Settings
from tags_metadata import metadata

app = FastAPI(openapi_tags=metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ALLOW_ORIGINS,
    allow_credentials=Settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=Settings.CORS_ALLOW_METHODS,
    allow_headers=Settings.CORS_ALLOW_HEADERS,
)

app.add_exception_handler(BackendError, backend_error_handler)  # type: ignore
app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,  # type: ignore
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,  # type: ignore
)
app.add_exception_handler(
    ValidationError,
    validation_exception_handler,  # type: ignore
)

app.include_router(users_router)
app.include_router(adv_router)
