"""Project SQLAlchemy orm services."""

from typing import Any

from sqlalchemy import Executable
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Sequence

from apps.common.common_types import ModelType


class StatementExecutor:
    """Async CRUD operations."""

    async def execute_return_statement(
        self,
        session: AsyncSession,
        statement: Executable,
        commit: bool = False,
        many: bool = False,
    ) -> ModelType | Sequence[ModelType] | None:
        """Execute statement with returning data."""
        alchemy_result: Result[Any] = await session.execute(statement)
        if commit:
            await session.commit()
        if many:
            return alchemy_result.scalars().all()
        return alchemy_result.scalar_one_or_none()

    async def execute_delete_statement(
        self,
        session: AsyncSession,
        statement: Executable,
    ) -> None:
        """Execute delete statement."""
        await session.execute(statement)
        await session.commit()


statement_executor = StatementExecutor()
