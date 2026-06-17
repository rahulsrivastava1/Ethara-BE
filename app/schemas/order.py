from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def validate_unique_products(
        cls, items: list[OrderItemCreate]
    ) -> list[OrderItemCreate]:
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Each product can only appear once per order")
        return items


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: str
    customer_id: int
    total_amount: Decimal
    total_items: int
    created_at: datetime
    items: list[OrderItemResponse]


class OrderItemSummaryResponse(BaseModel):
    product_name: str
    sku: str
    qty: int
    unit_price: Decimal
    total_price: Decimal


class OrderListResponse(BaseModel):
    id: int
    order_id: str
    customer_name: str
    total_amount: Decimal
    total_items: int
    items: list[OrderItemSummaryResponse]
