"""0001

Revision ID: 9ab9ca504f05
Revises: a97455bbb83a
Create Date: 2024-05-14 18:49:29.853617

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9ab9ca504f05"
down_revision: Union[str, None] = "a97455bbb83a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade db."""
    op.create_table(
        "advertisement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("run", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=100), nullable=True),
        sa.Column("salon", sa.String(length=50), nullable=True),
        sa.Column("seller", sa.String(length=255), nullable=False),
        sa.Column("adv_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("advertisement_pkey")),
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade db."""
    op.drop_table("advertisement")
    # ### end Alembic commands ###
