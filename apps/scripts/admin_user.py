"""Admin user creation."""

import logging

from apps.common.dependencies import get_session
from apps.user.handlers import user_handlers
from apps.user.schemas import CreateAdminUserIn
from settings import Settings

logger = logging.getLogger(__name__)


def create_admin_user_logic() -> None:
    """Create admin user."""
    session = next(get_session())
    schema = CreateAdminUserIn(
        username=Settings.DB_ADMIN_USERNAME,
        email=Settings.DB_ADMIN_EMAIL,
        password_check=Settings.DB_ADMIN_PASSWORD,
        password_re_check=Settings.DB_ADMIN_PASSWORD,
        is_active=True,
        is_admin=True,
    )
    user_handlers.sync_create_admin_user(schema, session)
    logger.info('Admin user successfully created.')


def create_admin_user() -> None:
    """Create admin user with catching errors."""
    try:
        create_admin_user_logic()
    except Exception as ex:
        logger.info(str(ex))


if __name__ == '__main__':
    create_admin_user()
