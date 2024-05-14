"""Advertisement apps handlers."""

from typing import Any, Sequence

from fastapi import Request
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.schemas import AdvPeriodQuerySchema
from apps.advertisements.statements import adv_statements
from apps.common.orm_services import statement_executor as executor


class AdvHandlers:
    """Advertisement handlers."""

    async def get_adv_period_list(
        self,
        request: Request,
        session: AsyncSession,
        period: AdvPeriodQuerySchema,
    ) -> list[Any] | Sequence[list[Any]] | None:
        """Handle request of getting advertisement period list."""
        statement: Executable = adv_statements.period_list_statement(period=period)
        return await executor.execute_return_statement(
            session,
            statement,
            many=True,
        )


adv_handlers = AdvHandlers()
