"""Advertisement apps statements."""

from datetime import datetime

from sqlalchemy import Executable, delete, func, select

from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import (
    AdvNameModelQuerySchema,
    AdvPeriodQuerySchema,
    UrlSchema,
)
from apps.common.base_statements import BaseCRUDStatements


class AdvStatements(BaseCRUDStatements):
    """Statements for Advertisement model."""

    def period_list_statement(
        self,
        *,
        period: AdvPeriodQuerySchema,
    ) -> Executable:
        """Get period advertisement list."""
        select_statement = select(self.model)
        if period.begin:
            select_statement = select_statement.filter(
                self.model.adv_date >= period.begin,
            )
        if period.end:
            select_statement = select_statement.filter(
                self.model.adv_date <= period.end,
            )
        return select_statement.execution_options(populate_existing=True)

    def name_model_stat_statement(
        self,
        *,
        car_info: AdvNameModelQuerySchema,
    ) -> Executable:
        """Get name/model stat statement with car_info schema filters."""
        statement = select(self.model).with_only_columns(
            self.model.price,
            self.model.adv_date,
        )
        if car_info.name:
            statement = statement.where(
                func.lower(self.model.name) == car_info.name.lower(),
            )
        if car_info.model:
            statement = statement.where(
                func.lower(self.model.model) == car_info.model.lower(),
            )
        return statement.execution_options(populate_existing=True)

    def delete_old_statement(
        self,
        old_date: datetime,
    ) -> Executable:
        """Create statement for deleting old advertisements."""
        return delete(self.model).where(self.model.created_at <= old_date)

    def get_adv_by_url_statement(
        self,
        url: UrlSchema,
    ) -> Executable:
        """Create statement for getting advertisement by url."""
        return select(self.model).filter(self.model.url.endswith(url.url))


adv_statements = AdvStatements(model=Advertisement)
