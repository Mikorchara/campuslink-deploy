from datetime import datetime

from pydantic import BaseModel, Field


class LikeState(BaseModel):
    count: int
    liked: bool


class NotificationRead(BaseModel):
    id: int
    kind: str
    message: str
    is_read: bool
    created_at: datetime
    link: str | None


class NotificationPage(BaseModel):
    items: list[NotificationRead]
    total: int
    page: int
    page_size: int
    unread_count: int


class ReadAll(BaseModel):
    up_to_id: int = Field(ge=1)
