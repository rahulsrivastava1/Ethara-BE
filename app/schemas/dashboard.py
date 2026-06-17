from pydantic import BaseModel

from app.schemas.product import ProductResponse


class DashboardResponse(BaseModel):
    total_products: int
    total_customers: int
    total_orders: int
    low_stock_products: list[ProductResponse]
