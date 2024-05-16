"""Utilities for saving date to db."""

from apps.advertisements.handlers import adv_handlers
from apps.advertisements.schemas import CreateAdvIn
from apps.common.dependencies import get_session


def save_adv_data_to_db(adv_data: dict) -> None:
    """Save data to db."""
    session = next(get_session())
    schema = CreateAdvIn(**adv_data)
    adv_handlers.create_adv(session, schema)


def save_adv_data(adv_data: dict) -> str:
    """Save data with catching errors."""
    message = 'Successfully saved data to db.'
    try:
        save_adv_data_to_db(adv_data)
    except Exception as ex:
        message = str(ex)
    return message
