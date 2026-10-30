from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.core.exceptions import AppError
from src.models.activity import Notification, PostLike, ProductLike
from src.models.forum import ForumPost
from src.models.product import Product
from src.models.transaction import TransactionRequest
from src.models.user import User


def insert_once(db: Session, model, values: dict, unique_columns: list[str]) -> bool:
    # Both supported databases implement conflict handling in the database, so
    # concurrent retries cannot create duplicate likes or messages.
    if db.get_bind().dialect.name == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    result = db.execute(insert(model).values(**values).on_conflict_do_nothing(
        index_elements=unique_columns).returning(model.id))
    return result.scalar_one_or_none() is not None


def notify(db: Session, *, recipient_id: int, actor_id: int, event_key: str,
           kind: str, message: str, target_type: str, target_id: int) -> None:
    if recipient_id == actor_id:
        return
    insert_once(db, Notification, dict(recipient_id=recipient_id, event_key=event_key,
        kind=kind, message=message[:350], target_type=target_type, target_id=target_id,
        is_read=False), ['event_key'])


def like_target(db: Session, kind: str, target_id: int, *, lock=False):
    model = Product if kind == 'product' else ForumPost
    query = select(model).where(model.id == target_id)
    if lock:
        query = query.with_for_update()
    target = db.scalar(query)
    if target is None:
        raise AppError(404, '商品不存在或已删除' if kind == 'product' else '帖子不存在或已删除')
    return target


def like_state(db: Session, kind: str, target_id: int, user_id: int | None) -> dict:
    model, column = (ProductLike, ProductLike.product_id) if kind == 'product' else (PostLike, PostLike.post_id)
    count = db.scalar(select(func.count()).select_from(model).where(column == target_id))
    liked = user_id is not None and db.scalar(select(model.id).where(column == target_id, model.user_id == user_id)) is not None
    return dict(count=count, liked=liked)


def set_like(db: Session, kind: str, target_id: int, user: User, enabled: bool) -> dict:
    target = like_target(db, kind, target_id, lock=True)
    model, column = (ProductLike, ProductLike.product_id) if kind == 'product' else (PostLike, PostLike.post_id)
    if enabled:
        inserted = insert_once(db, model, {'user_id': user.id, column.key: target_id}, ['user_id', column.key])
        if inserted:
            owner = target.seller_id if kind == 'product' else target.author_id
            label = '商品' if kind == 'product' else '帖子'
            notify(db, recipient_id=owner, actor_id=user.id, event_key=f'like:{kind}:{target_id}:{user.id}',
                kind=kind + '_like', message=f'{user.username} 赞了你的{label}《{target.title}》',
                target_type=kind, target_id=target_id)
    else:
        db.execute(delete(model).where(column == target_id, model.user_id == user.id))
    db.commit()
    return like_state(db, kind, target_id, user.id)


def unread_count(db: Session, user_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Notification).where(
        Notification.recipient_id == user_id, Notification.is_read.is_(False)))


def read_notification(db: Session, item: Notification) -> dict:
    model = {'product': Product, 'post': ForumPost, 'transaction': TransactionRequest}[item.target_type]
    exists = db.scalar(select(model.id).where(model.id == item.target_id)) is not None
    # Do not preserve personal comment bodies or contact details in messages.
    link = {'product': f'/product/{item.target_id}', 'post': f'/forum/{item.target_id}',
            'transaction': f'/transactions?transaction={item.target_id}'}[item.target_type] if exists else None
    return dict(id=item.id, kind=item.kind, message=item.message, is_read=item.is_read,
                created_at=item.created_at, link=link)
