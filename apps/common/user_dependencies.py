"""User specific dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated, Sequence

from apps.common.common_utilities import checkers, get_token_data
from apps.common.dependencies import get_async_session
from apps.common.exceptions import BackendError
from apps.common.orm_services import statement_executor
from apps.user.models import User
from apps.user.statements import user_crud_statements

reusable_oauth = OAuth2PasswordBearer(tokenUrl='/login/', scheme_name='JWT')


async def get_user(
    token: str,
    session: AsyncSession,
    is_admin: bool = False,
) -> User:
    """Get current average or admin user with given token and is_admin flag."""
    try:
        token_data = get_token_data(token)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Credential verification failed',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    read_user_stmt = user_crud_statements.read_statement(
        obj_data={'email': token_data.sub},
    )
    user: User | Sequence[User | None] | None = (
        await statement_executor.execute_return_statement(
            session,
            read_user_stmt,
        )
    )
    checked_user: User = checkers.check_created_instance(user, 'User')
    if is_admin and not checked_user.is_admin:
        raise BackendError(
            message='User is not admin user',
            code=status.HTTP_403_FORBIDDEN,
        )
    return checked_user


async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """Get current user with given token."""
    return await get_user(token, session)


async def get_current_admin_user(
    token: Annotated[str, Depends(reusable_oauth)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """Get current admin user with given token."""
    return await get_user(token, session, is_admin=True)
