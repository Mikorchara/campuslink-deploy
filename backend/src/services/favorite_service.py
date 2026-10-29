from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.core.exceptions import AppError
from src.models.favorite import Favorite
from src.models.product import Product
from src.models.user import User
from src.schemas.favorite import FavoriteRead
from src.services.product_service import get_product, serialize_product


def add_favorite(db: Session, user: User, product_id: int) -> Favorite:
    product = get_product(db, product_id)
    if product.seller_id == user.id:
        raise AppError(400, "不能收藏自己发布的商品")
    existing = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.product_id == product_id
        )
    )
    if existing:
        return existing
    favorite = Favorite(user_id=user.id, product_id=product_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user: User, product_id: int) -> None:
    favorite = db.scalar(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.product_id == product_id
        )
    )
    if favorite:
        db.delete(favorite)
        db.commit()


def is_favorited(db: Session, user: User, product_id: int) -> bool:
    get_product(db, product_id)
    return (
        db.scalar(
            select(Favorite.id).where(
                Favorite.user_id == user.id, Favorite.product_id == product_id
            )
        )
        is not None
    )


def list_favorites(db: Session, user: User) -> list[FavoriteRead]:
    favorites = list(
        db.scalars(
            select(Favorite)
            .options(
                selectinload(Favorite.product).selectinload(Product.seller)
            )
            .where(Favorite.user_id == user.id)
            .order_by(Favorite.created_at.desc())
        ).all()
    )
    return [
        FavoriteRead(
            id=favorite.id,
            product=serialize_product(favorite.product),
            created_at=favorite.created_at,
        )
        for favorite in favorites
    ]

