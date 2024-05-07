"""Authorization apps routers."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from apps.authorization.handlers import authorization_handlers
from apps.authorization.schemas import AuthOut
from apps.common.dependencies import get_async_session

authorization_router = APIRouter()


@authorization_router.post(
    '/login/',
    name='login',
    response_model=AuthOut,
    summary='Create access and refresh token',
    responses={},
    tags=['Authorization application'],
)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthOut:
    """
    **Login user**.

    **Input:**
    - **username:** login, which consists of name and random number; required
    - **password:** password to this login name; required

    **Return:**
    - **access_token:** token for access to endpoints
    - **refresh_token:** token for refresh access token
    - **user_id:** id of logged-in user
    """
    return await authorization_handlers.login(
        request=request,
        form_data=form_data,
        session=session,
    )
