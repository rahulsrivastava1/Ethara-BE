"""add total_price to order_items

Revision ID: 9d8219da1ff5
Revises: 5d8ed497bb36
Create Date: 2026-06-17 23:05:25.263203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d8219da1ff5'
down_revision: Union[str, None] = '5d8ed497bb36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'order_items',
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.execute(
        "UPDATE order_items SET total_price = unit_price * quantity"
    )
    op.alter_column('order_items', 'total_price', nullable=False)


def downgrade() -> None:
    op.drop_column('order_items', 'total_price')
