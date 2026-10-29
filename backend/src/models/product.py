from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.favorite import Favorite
    from src.models.transaction import TransactionRequest
    from src.models.user import User


class ProductStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    OFFLINE = "OFFLINE"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(50), index=True)
    image_url: Mapped[str] = mapped_column(
        String(500), default="/assets/images/goods_math_book.png"
    )
    status: Mapped[ProductStatus] = mapped_column(
        SqlEnum(ProductStatus, native_enum=False, length=20),
        default=ProductStatus.AVAILABLE,
        index=True,
    )
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    seller: Mapped["User"] = relationship(back_populates="products")
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    transaction_requests: Mapped[list["TransactionRequest"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

