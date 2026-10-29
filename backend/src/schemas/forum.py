from datetime import datetime
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.user import SellerInfo

ForumCategory = Literal["备考", "新生", "宿舍", "学习", "生活"]


class PostWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=10000)
    category: ForumCategory
    image_url: str = Field(default="", max_length=500)

    @field_validator("image_url")
    @classmethod
    def local_image_only(cls, value: str) -> str:
        if value and not re.fullmatch(r"(?:/api/uploads/[0-9a-f]{32}\.webp|/assets/images/[a-zA-Z0-9_-]+\.(?:png|jpg|webp))", value):
            raise ValueError("请使用平台上传的封面图片")
        return value


class CommentWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    content: str = Field(min_length=1, max_length=1000)


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    summary: str
    category: ForumCategory
    tag: str
    tagType: str
    image_url: str
    author: SellerInfo
    comment_count: int
    created_at: datetime
    updated_at: datetime
    created_date: str


class CommentRead(BaseModel):
    id: int
    post_id: int
    content: str
    author: SellerInfo
    created_at: datetime
    updated_at: datetime


class PostPage(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    page_size: int


class CommentPage(BaseModel):
    items: list[CommentRead]
    total: int
    page: int
    page_size: int
