"""0002

Revision ID: c7e108355df9
Revises: 9ab9ca504f05
Create Date: 2024-05-14 19:44:56.116389

"""

from typing import Sequence, Union

from sqlalchemy import delete, insert

from alembic import op
from apps.authorization.auth_utilities import get_hashed_password
from apps.user.models import User
from settings import Settings

# revision identifiers, used by Alembic.
revision: str = "c7e108355df9"
down_revision: Union[str, None] = "9ab9ca504f05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade db."""
    if Settings.DB_ADMIN_USERNAME:
        password = get_hashed_password(Settings.DB_ADMIN_PASSWORD)
        op.execute(
            insert(User).values(
                {
                    'id': 1,
                    'username': Settings.DB_ADMIN_USERNAME,
                    'password': password,
                    'email': Settings.DB_ADMIN_EMAIL,
                    'is_active': True,
                    'is_admin': True,
                },
            ),
        )


def downgrade() -> None:
    """Downgrade db."""
    op.execute(delete(User).where(User.id == 1))
    # ### end Alembic commands ###
