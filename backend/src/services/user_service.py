from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.core.exceptions import AppError
from src.models.user import User
from src.schemas.user import SellerContact, UserRead, UserUpdate


def serialize_user(user: User) -> UserRead:
    return UserRead.model_validate(user)


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    changes = payload.model_dump(exclude_unset=True)

    username = changes.get("username")
    email = changes.get("email")
    if username or email:
        conditions = []
        if username:
            conditions.append(User.username == username)
        if email:
            conditions.append(User.email == email)
        existing = db.scalar(
            select(User).where(or_(*conditions), User.id != user.id)
        )
        if existing:
            if username and existing.username == username:
                raise AppError(409, "用户名已被使用")
            raise AppError(409, "邮箱已被注册")

    for field, value in changes.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def serialize_contact(user: User) -> SellerContact:
    return SellerContact(
        id=user.id,
        name=user.username,
        avatar=user.avatar,
        email=user.email,
        contact=user.contact,
    )

