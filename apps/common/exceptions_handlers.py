"""App exceptions handlers."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.common.enum import JSENDStatus
from apps.common.exceptions import BackendError
from settings import Settings


def backend_error_handler(request: Request, exc: BackendError) -> Response:
    """Return result from Back-end exception."""
    return JSONResponse(content=exc.dict(), status_code=exc.code)


def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Get the original 'detail', 'status_code' and 'headers'."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': JSENDStatus.FAIL,
            'data': exc.detail,
            'message': 'Validation error.',
            'code': exc.status_code,
        },
        headers=exc.headers,
    )


def integrity_error_handler(error: IntegrityError) -> None:
    """Raise error from IntegrityError."""
    if 'duplicate' in error.args[0]:
        if error.orig is None:
            error_message = 'Integrity error'
        else:
            error_message = error.orig.args[0].split('\n')[-1]
        raise BackendError(
            message=str(error_message) if Settings.DEBUG else 'Update error.',
        )
    else:
        raise BackendError(  # noqa: WPS503
            message=str(error) if Settings.DEBUG else 'Internal server error.',
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status=JSENDStatus.ERROR,
        )


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError,
) -> JSONResponse:
    """Get the original 'detail' list of errors."""
    details = exc.errors()
    modified_details = []
    for error in details:
        modified_details.append(
            {
                'location': error['loc'],
                'message': error['msg'].capitalize(),
                'type': error['type'],
                'context': str(error.get('ctx', None)),
            },
        )
    return JSONResponse(
        content={
            'status': JSENDStatus.FAIL,
            'data': modified_details,
            'message': 'Validation error.',
            'code': status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
