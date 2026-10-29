from datetime import datetime

from pydantic import BaseModel, Field

from src.models.transaction import TransactionStatus


class TransactionCreate(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class TransactionStatusUpdate(BaseModel):
    status: TransactionStatus


class TransactionRead(BaseModel):
    id: int
    product_id: int
    product_title: str
    buyer_id: int
    buyer_name: str
    seller_id: int
    seller_name: str
    status: TransactionStatus
    note: str | None = None
    created_at: datetime
    updated_at: datetime

