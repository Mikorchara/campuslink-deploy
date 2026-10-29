from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session, selectinload

from src.core.exceptions import AppError
from src.models.product import Product, ProductStatus
from src.models.transaction import TransactionRequest, TransactionStatus
from src.models.user import User
from src.schemas.transaction import TransactionCreate, TransactionRead
from src.services.product_service import get_product


def serialize_transaction(item: TransactionRequest) -> TransactionRead:
    return TransactionRead(
        id=item.id,
        product_id=item.product_id,
        product_title=item.product.title,
        buyer_id=item.buyer_id,
        buyer_name=item.buyer.username,
        seller_id=item.seller_id,
        seller_name=item.seller.username,
        status=item.status,
        note=item.note,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _load_transaction(db: Session, transaction_id: int) -> TransactionRequest:
    item = db.scalar(
        select(TransactionRequest)
        .options(
            selectinload(TransactionRequest.product),
            selectinload(TransactionRequest.buyer),
            selectinload(TransactionRequest.seller),
        )
        .where(TransactionRequest.id == transaction_id)
    )
    if item is None:
        raise AppError(404, "交易请求不存在")
    return item


def create_transaction(
    db: Session,
    buyer: User,
    product_id: int,
    payload: TransactionCreate,
) -> TransactionRequest:
    product = get_product(db, product_id)
    if product.seller_id == buyer.id:
        raise AppError(400, "不能购买自己发布的商品")
    if product.status != ProductStatus.AVAILABLE:
        raise AppError(409, "该商品当前不可预订")

    pending = db.scalar(
        select(TransactionRequest).where(
            TransactionRequest.product_id == product_id,
            TransactionRequest.buyer_id == buyer.id,
            TransactionRequest.status == TransactionStatus.PENDING,
        )
    )
    if pending:
        raise AppError(409, "你已发起过待处理的交易请求")

    item = TransactionRequest(
        product_id=product.id,
        buyer_id=buyer.id,
        seller_id=product.seller_id,
        note=payload.note,
    )
    db.add(item)
    db.commit()
    return _load_transaction(db, item.id)


def list_transactions(db: Session, user: User) -> list[TransactionRequest]:
    return list(
        db.scalars(
            select(TransactionRequest)
            .options(
                selectinload(TransactionRequest.product),
                selectinload(TransactionRequest.buyer),
                selectinload(TransactionRequest.seller),
            )
            .where(
                or_(
                    TransactionRequest.buyer_id == user.id,
                    TransactionRequest.seller_id == user.id,
                )
            )
            .order_by(TransactionRequest.created_at.desc())
        ).all()
    )


def update_transaction_status(
    db: Session,
    user: User,
    transaction_id: int,
    new_status: TransactionStatus,
) -> TransactionRequest:
    item = _load_transaction(db, transaction_id)
    allowed = {
        TransactionStatus.PENDING: {
            TransactionStatus.ACCEPTED,
            TransactionStatus.REJECTED,
            TransactionStatus.CANCELLED,
        },
        TransactionStatus.ACCEPTED: {
            TransactionStatus.COMPLETED,
            TransactionStatus.CANCELLED,
        },
    }
    if new_status not in allowed.get(item.status, set()):
        raise AppError(409, f"交易状态不能从 {item.status.value} 变更为 {new_status.value}")

    if new_status in {TransactionStatus.ACCEPTED, TransactionStatus.REJECTED}:
        if user.id != item.seller_id:
            raise AppError(403, "只有卖家可以接受或拒绝交易请求")
    elif new_status == TransactionStatus.CANCELLED:
        if user.id not in {item.buyer_id, item.seller_id}:
            raise AppError(403, "无权取消该交易")
    elif new_status == TransactionStatus.COMPLETED:
        if user.id != item.seller_id:
            raise AppError(403, "只有卖家可以确认交易完成")

    previous_status = item.status
    changed = db.execute(
        update(TransactionRequest)
        .where(TransactionRequest.id == item.id, TransactionRequest.status == previous_status)
        .values(status=new_status)
    )
    if changed.rowcount != 1:
        db.rollback()
        raise AppError(409, "交易状态已变化，请刷新后重试")

    if new_status == TransactionStatus.ACCEPTED:
        reserved = db.execute(
            update(Product)
            .where(Product.id == item.product_id, Product.status == ProductStatus.AVAILABLE)
            .values(status=ProductStatus.RESERVED)
        )
        if reserved.rowcount != 1:
            db.rollback()
            raise AppError(409, "商品已被预订或不再在售，请刷新")
    elif new_status == TransactionStatus.COMPLETED:
        completed = db.execute(
            update(Product)
            .where(Product.id == item.product_id, Product.status == ProductStatus.RESERVED)
            .values(status=ProductStatus.SOLD)
        )
        if completed.rowcount != 1:
            db.rollback()
            raise AppError(409, "商品状态已变化，无法确认完成")
    elif new_status == TransactionStatus.CANCELLED and previous_status == TransactionStatus.ACCEPTED:
        db.execute(
            update(Product)
            .where(Product.id == item.product_id, Product.status == ProductStatus.RESERVED)
            .values(status=ProductStatus.AVAILABLE)
        )

    db.commit()
    return _load_transaction(db, item.id)

