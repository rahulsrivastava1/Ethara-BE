from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.is_active.is_(True))
        .scalar()
        or 0
    )
    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.is_active.is_(True))
        .scalar()
        or 0
    )
    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.is_active.is_(True))
        .scalar()
        or 0
    )
    low_stock_products = (
        db.query(Product)
        .filter(
            Product.is_active.is_(True),
            Product.available_qty <= settings.low_stock_threshold,
        )
        .order_by(Product.available_qty, Product.id)
        .all()
    )

    return DashboardResponse(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_products=low_stock_products,
    )
