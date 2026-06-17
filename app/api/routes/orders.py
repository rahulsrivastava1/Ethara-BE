from decimal import Decimal
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderItemSummaryResponse,
    OrderListResponse,
    OrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def _generate_order_id(db: Session) -> str:
    for _ in range(20):
        order_id = f"ORD-{secrets.randbelow(10000):04d}"
        exists = db.query(Order.id).filter(Order.order_id == order_id).first()
        if exists is None:
            return order_id
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique order ID",
    )


def _build_order_list_response(order: Order) -> OrderListResponse:
    return OrderListResponse(
        id=order.id,
        order_id=order.order_id,
        customer_name=order.customer.full_name,
        total_amount=order.total_amount,
        total_items=order.total_items,
        items=[
            OrderItemSummaryResponse(
                product_name=item.product.product_name,
                sku=item.product.sku_code,
                qty=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in order.items
        ],
    )


def _build_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_id=order.order_id,
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        total_items=order.total_items,
        created_at=order.created_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in order.items
        ],
    )


def _get_order_or_404(db: Session, order_id: int) -> Order:
    order = (
        db.query(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items).selectinload(OrderItem.product),
        )
        .filter(Order.id == order_id, Order.is_active.is_(True))
        .first()
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)) -> OrderResponse:
    customer = (
        db.query(Customer)
        .filter(Customer.id == order_in.customer_id, Customer.is_active.is_(True))
        .first()
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    product_ids = [item.product_id for item in order_in.items]
    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids), Product.is_active.is_(True))
        .with_for_update()
        .all()
    )
    products_by_id = {product.id: product for product in products}

    if len(products_by_id) != len(product_ids):
        missing_ids = set(product_ids) - set(products_by_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product(s) not found: {sorted(missing_ids)}",
        )

    total_amount = Decimal("0.00")
    total_items = 0
    order_items: list[OrderItem] = []

    for item_in in order_in.items:
        product = products_by_id[item_in.product_id]
        if product.available_qty < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient inventory for product "
                    f"({product.product_name}): "
                    f"requested {item_in.quantity}, available {product.available_qty}"
                ),
            )

        line_total = product.price * item_in.quantity
        total_amount += line_total
        total_items += item_in.quantity
        product.available_qty -= item_in.quantity
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item_in.quantity,
                unit_price=product.price,
                total_price=line_total,
            )
        )

    order = Order(
        customer_id=order_in.customer_id,
        total_amount=total_amount,
        total_items=total_items,
        order_id=_generate_order_id(db),
        items=order_items,
    )
    db.add(order)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    order = _get_order_or_404(db, order.id)
    return _build_order_response(order)


@router.get("", response_model=list[OrderListResponse])
def list_orders(db: Session = Depends(get_db)) -> list[OrderListResponse]:
    orders = (
        db.query(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items).selectinload(OrderItem.product),
        )
        .filter(Order.is_active.is_(True))
        .order_by(Order.id)
        .all()
    )
    return [_build_order_list_response(order) for order in orders]


@router.get("/{order_id}", response_model=OrderListResponse)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderListResponse:
    order = _get_order_or_404(db, order_id)
    return _build_order_list_response(order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)) -> None:
    order = _get_order_or_404(db, order_id)

    product_ids = [item.product_id for item in order.items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).with_for_update().all()
    products_by_id = {product.id: product for product in products}

    for item in order.items:
        product = products_by_id[item.product_id]
        product.available_qty += item.quantity

    order.is_active = False

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
