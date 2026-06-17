"""add total_items to orders

Revision ID: fa81679d2dbe
Revises: bf0657786b48
Create Date: 2026-06-17 22:58:06.341393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa81679d2dbe'
down_revision: Union[str, None] = 'bf0657786b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('total_items', sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE orders
        SET total_items = (
            SELECT COALESCE(SUM(quantity), 0)
            FROM order_items
            WHERE order_items.order_id = orders.id
        )
        """
    )

    op.alter_column('orders', 'total_items', nullable=False)


def downgrade() -> None:
    op.drop_column('orders', 'total_items')
