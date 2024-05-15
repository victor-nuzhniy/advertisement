"""Advertisement apps statements."""

from sqlalchemy import Executable, select

from apps.advertisements.models import Advertisement
from apps.advertisements.schemas import AdvPeriodQuerySchema
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


adv_statements = AdvStatements(model=Advertisement)
