from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from src.core.exceptions import AppError
from src.models.product import Product, ProductStatus
from src.models.transaction import TransactionRequest, TransactionStatus
from src.models.user import User
from src.schemas.product import ProductCreate, ProductRead, ProductUpdate
from src.schemas.user import SellerInfo


def _relative_time(created_at: datetime) -> str:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    seconds = max(0, int((datetime.now(timezone.utc) - created_at).total_seconds()))
    if seconds < 60:
        return "刚刚"
    if seconds < 3600:
        return f"{seconds // 60}分钟前"
    if seconds < 86400:
        return f"{seconds // 3600}小时前"
    if seconds < 86400 * 7:
        return f"{seconds // 86400}天前"
    return created_at.strftime("%Y-%m-%d")


def serialize_product(product: Product) -> ProductRead:
    return ProductRead(
        id=product.id,
        title=product.title,
        description=product.description,
        price=float(product.price),
        category=product.category,
        image_url=product.image_url,
        status=product.status,
        location=product.location,
        seller=SellerInfo(
            id=product.seller.id,
            name=product.seller.username,
            avatar=product.seller.avatar,
        ),
        time_ago=_relative_time(product.created_at),
        created_at=product.created_at,
    )


def list_products(
    db: Session,
    *,
    seller_id: int | None = None,
    keyword: str | None = None,
    category: str | None = None,
    status: ProductStatus | None = None,
    page: int = 1,
    page_size: int = 20,
) -> list[Product]:
    statement = select(Product).options(selectinload(Product.seller))

    if seller_id is not None:
        statement = statement.where(Product.seller_id == seller_id)
    if keyword:
        pattern = f"%{keyword.strip()}%"
        statement = statement.where(
            or_(Product.title.ilike(pattern), Product.description.ilike(pattern))
        )
    if category and category != "全部":
        statement = statement.where(Product.category == category)
    if status:
        statement = statement.where(Product.status == status)

    statement = (
        statement.order_by(Product.created_at.desc(), Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(db.scalars(statement).all())


def get_product(db: Session, product_id: int) -> Product:
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.seller))
        .where(Product.id == product_id)
    )
    if product is None:
        raise AppError(404, "商品不存在")
    return product


def create_product(db: Session, seller: User, payload: ProductCreate) -> Product:
    product = Product(seller_id=seller.id, **payload.model_dump())
    db.add(product)
    db.commit()
    return get_product(db, product.id)


def _ensure_owner(product: Product, user: User) -> None:
    if product.seller_id != user.id:
        raise AppError(403, "只能管理自己发布的商品")


def update_product(
    db: Session,
    product_id: int,
    user: User,
    payload: ProductUpdate,
) -> Product:
    product = get_product(db, product_id)
    _ensure_owner(product, user)
    if payload.status is not None:
        _ensure_status_editable(db, product, payload.status)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    return get_product(db, product.id)


def set_product_status(
    db: Session,
    product_id: int,
    user: User,
    status: ProductStatus,
) -> Product:
    product = get_product(db, product_id)
    _ensure_owner(product, user)
    _ensure_status_editable(db, product, status)
    product.status = status
    db.commit()
    return get_product(db, product.id)


def _ensure_status_editable(db: Session, product: Product, status: ProductStatus) -> None:
    active = db.scalar(select(TransactionRequest.id).where(
        TransactionRequest.product_id == product.id,
        TransactionRequest.status == TransactionStatus.ACCEPTED,
    ))
    if active is not None and status != ProductStatus.RESERVED:
        raise AppError(409, "商品有已接受的交易，请先在我的交易中完成或取消")


def delete_product(db: Session, product_id: int, user: User) -> None:
    product = get_product(db, product_id)
    _ensure_owner(product, user)
    db.delete(product)
    db.commit()

