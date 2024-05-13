"""User apps handlers."""

from fastapi import Request
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Sequence

from apps.common.common_utilities import checkers
from apps.common.orm_services import statement_executor as executor
from apps.user.models import User
from apps.user.schemas import CreateUserIn, CreateUserOut
from apps.user.statements import user_crud_statements


class UserHandlers:
    """User handlers."""

    async def create_user(
        self,
        request: Request,
        user: CreateUserIn,
        session: AsyncSession,
    ) -> CreateUserOut:
        """Create user with given data."""
        statement: Executable = user_crud_statements.create_statement(
            obj_data={
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'is_active': False,
            },
        )
        created_user: User | Sequence[User | None] | None = (
            await executor.execute_return_statement(
                session,
                statement,
                commit=True,
            )
        )
        checked_user: User = checkers.check_created_instance(created_user, 'User')
        return CreateUserOut.model_validate(checked_user)


user_handlers = UserHandlers()
