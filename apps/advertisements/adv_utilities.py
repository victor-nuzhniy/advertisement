"""Auxiliary functionality of advertisement apps."""

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from dateutil.relativedelta import relativedelta


@dataclass
class AdvStat:
    """Advertisement statistical data."""

    min_price: int = 100000000
    max_price: int = 0
    num_day: int = 0
    num_week: int = 0
    num_month: int = 0


class AdvAuxiliaryFunc:
    """Auxiliary functionality for advertisement apps."""

    def get_statistical_info(self, model_data: Sequence) -> AdvStat:
        """
        Get statistical model data.

        :param model_data: Sequence Advertisement model data, selected with filters.
        :return: AdvStat instance.
        """
        stat_data = AdvStat()
        day_ago = date.today() + relativedelta(days=-1)
        week_ago = date.today() + relativedelta(days=-7)
        month_ago = date.today() + relativedelta(months=-1)
        for model in model_data:
            stat_data.min_price = min(stat_data.min_price, model.price)
            stat_data.max_price = max(stat_data.max_price, model.price)
            if model.adv_date >= day_ago:
                stat_data.num_day += 1
            if model.adv_date >= week_ago:
                stat_data.num_week += 1
            if model.adv_date >= month_ago:
                stat_data.num_month += 1
        return stat_data


adv_auxiliary_func = AdvAuxiliaryFunc()
