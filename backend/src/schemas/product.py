from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from src.models.product import ProductStatus
from src.schemas.user import SellerInfo


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    category: str = Field(min_length=1, max_length=50)
    image_url: str = Field(
        default="/assets/images/goods_math_book.png", max_length=500
    )
    location: str | None = Field(default=None, max_length=120)

    @field_validator("title", "category")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("字段不能为空")
        return value


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(
        default=None, gt=0, max_digits=10, decimal_places=2
    )
    category: str | None = Field(default=None, min_length=1, max_length=50)
    image_url: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=120)
    status: ProductStatus | None = None


class ProductStatusUpdate(BaseModel):
    status: ProductStatus


class ProductRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: float
    category: str
    image_url: str
    status: ProductStatus
    location: str | None = None
    seller: SellerInfo
    time_ago: str
    created_at: datetime


class ProductListQuery(BaseModel):
    keyword: str | None = None
    category: str | None = None
    status: ProductStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

