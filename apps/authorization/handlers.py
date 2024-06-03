"""Authorization apps handlers."""

from typing import Any, Sequence

from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Executable
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from apps.authorization.auth_utilities import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_user,
)
from apps.authorization.schemas import AuthOut
from apps.common.common_utilities import refresh_access_token
from apps.common.orm_services import statement_executor
from apps.user.statements import user_crud_statements


class AuthorizationHandlers:
    """Handlers for authorization apps."""

    async def login(
        self,
        *,
        request: Request,
        form_data: OAuth2PasswordRequestForm,
        session: AsyncSession,
    ) -> AuthOut:
        """Login user with given credentials."""
        statement: Executable = user_crud_statements.read_statement(
            obj_data={'username': form_data.username},
        )
        user: Row[Any] | Sequence[Row[Any]] | None = (
            await statement_executor.execute_return_statement(
                session,
                statement,
            )
        )
        user = verify_user(user)
        if isinstance(user, Sequence):
            user = user[0]
        verify_password(user, form_data.password)
        return AuthOut(
            access_token=create_access_token(user.email),
            refresh_token=create_refresh_token(user.email),
            id=user.id,
        )

    def refresh(
        self,
        *,
        request: Request,
        refresh_token: str,
    ) -> str:
        """Refresh access token."""
        return refresh_access_token(refresh_token)


authorization_handlers = AuthorizationHandlers()
