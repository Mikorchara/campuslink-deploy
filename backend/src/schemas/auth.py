from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserRead


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class LoginData(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserRead

