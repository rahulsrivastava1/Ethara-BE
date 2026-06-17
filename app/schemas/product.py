from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    product_name: str
    sku_code: str
    price: Decimal
    available_qty: int = Field(ge=0, default=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
