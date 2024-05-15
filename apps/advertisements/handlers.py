"""Advertisement apps handlers."""

from typing import Any, Sequence

from fastapi import Request
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession

from apps.advertisements.adv_utilities import adv_auxiliary_func
from apps.advertisements.schemas import AdvNameModelQuerySchema, AdvPeriodQuerySchema
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

    async def get_name_model_stat(
        self,
        request: Request,
        session: AsyncSession,
        car_info: AdvNameModelQuerySchema,
    ) -> dict:
        """
        Handle request of getting name and model statistics.

        Statistics concerning min/max price and number/period.
        """
        statement: Executable = adv_statements.name_model_stat_statement(
            car_info=car_info,
        )
        advs = await executor.execute_fetchmany_statement(
            session,
            statement,
        )
        stat_data = adv_auxiliary_func.get_statistical_info(advs)
        return stat_data.__dict__


adv_handlers = AdvHandlers()
