from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.core.exceptions import AppError
from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.schemas.auth import LoginData, LoginRequest, RegisterRequest
from src.services.user_service import serialize_user


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.scalar(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
    )
    if existing:
        if existing.username == payload.username:
            raise AppError(409, "用户名已被使用")
        raise AppError(409, "邮箱已被注册")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> LoginData:
    user = db.scalar(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.username)
        )
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(401, "用户名或密码错误")
    if not user.is_active:
        raise AppError(403, "账号已被停用")

    return LoginData(
        token=create_access_token(user.id),
        user=serialize_user(user),
    )

