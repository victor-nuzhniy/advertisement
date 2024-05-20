"""Advertisement apps handlers."""

from datetime import datetime
from typing import Any, Sequence

from fastapi import Request
from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from apps.advertisements.adv_utilities import adv_auxiliary_func
from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import (
    AdvInList,
    AdvNameModelQuerySchema,
    AdvPeriodQuerySchema,
    CreateAdvIn,
    UrlSchema,
)
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

    async def bulk_create_adv(
        self,
        request: Request,
        session: AsyncSession,
        advs: AdvInList,
    ) -> None:
        """Create many advertisements."""
        statement: Executable = adv_statements.create_many_statement(advs)
        await executor.execute_return_statement(
            session,
            statement,
            commit=True,
            many=True,
        )

    def create_adv(
        self,
        session: Session,
        adv: CreateAdvIn,
    ) -> None:
        """Create single advertisement."""
        statement: Executable = adv_statements.create_statement(schema=adv)
        executor.sync_execute_return_statement(session, statement, commit=True)

    def delete_old_adv(
        self,
        session: Session,
        old_date: datetime,
    ) -> None:
        """Delete advertisements, older than argument."""
        statement: Executable = adv_statements.delete_old_statement(old_date=old_date)
        executor.sync_execute_delete_statement(session, statement)

    async def get_adv_by_url(
        self,
        request: Request,
        session: AsyncSession,
        url: UrlSchema,
    ) -> Any:
        """Get advertisement by url."""
        statement: Executable = adv_statements.get_adv_by_url_statement(url)
        advertisements: Advertisement | Sequence[Advertisement] | None = (
            await executor.execute_return_statement(
                session,
                statement,
                many=True,
            )
        )
        if advertisements:
            return advertisements[0]
        return None


adv_handlers = AdvHandlers()
