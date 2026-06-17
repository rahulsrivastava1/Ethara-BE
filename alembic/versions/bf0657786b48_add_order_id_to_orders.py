"""add order_id to orders

Revision ID: bf0657786b48
Revises: 1e893180b777
Create Date: 2026-06-17 22:44:35.443390

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf0657786b48'
down_revision: Union[str, None] = '1e893180b777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('order_id', sa.String(length=50), nullable=True))

    connection = op.get_bind()
    orders = connection.execute(sa.text("SELECT id, created_at FROM orders")).fetchall()
    for order in orders:
        date_part = order.created_at.strftime("%Y%m%d")
        connection.execute(
            sa.text("UPDATE orders SET order_id = :order_id WHERE id = :id"),
            {"order_id": f"ORD-{date_part}-{uuid4().hex[:8].upper()}", "id": order.id},
        )

    op.alter_column('orders', 'order_id', nullable=False)
    op.create_unique_constraint('uq_orders_order_id', 'orders', ['order_id'])


def downgrade() -> None:
    op.drop_constraint('uq_orders_order_id', 'orders', type_='unique')
    op.drop_column('orders', 'order_id')
