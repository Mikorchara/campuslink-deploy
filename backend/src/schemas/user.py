from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    contact: str | None = None
    bio: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = None
    avatar: str | None = Field(default=None, max_length=500)
    contact: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=255)


class SellerInfo(BaseModel):
    id: int
    name: str
    avatar: str


class SellerContact(BaseModel):
    id: int
    name: str
    avatar: str
    email: EmailStr
    contact: str | None = None

