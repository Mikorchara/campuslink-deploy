from datetime import datetime

from pydantic import BaseModel

from src.schemas.product import ProductRead


class FavoriteRead(BaseModel):
    id: int
    product: ProductRead
    created_at: datetime


class FavoriteState(BaseModel):
    product_id: int
    is_favorited: bool

