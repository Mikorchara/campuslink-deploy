from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update

from src.core.exceptions import AppError
from src.dependencies.auth import CurrentUser, DatabaseSession, get_optional_user
from src.models.activity import Notification
from src.models.user import User
from src.schemas.activity import LikeState, NotificationPage, ReadAll
from src.schemas.common import ApiResponse, success
from src.services.activity_service import like_state, like_target, read_notification, set_like, unread_count

router = APIRouter(tags=['Activity'])
OptionalUser = Annotated[User | None, Depends(get_optional_user)]


@router.get('/products/{target_id}/like', response_model=ApiResponse[LikeState])
def product_like(target_id: int, db: DatabaseSession, user: OptionalUser):
    like_target(db, 'product', target_id)
    return success(like_state(db, 'product', target_id, user.id if user else None))


@router.put('/products/{target_id}/like', response_model=ApiResponse[LikeState])
def add_product_like(target_id: int, db: DatabaseSession, user: CurrentUser):
    return success(set_like(db, 'product', target_id, user, True))


@router.delete('/products/{target_id}/like', response_model=ApiResponse[LikeState])
def remove_product_like(target_id: int, db: DatabaseSession, user: CurrentUser):
    return success(set_like(db, 'product', target_id, user, False))


@router.get('/forum/posts/{target_id}/like', response_model=ApiResponse[LikeState])
def post_like(target_id: int, db: DatabaseSession, user: OptionalUser):
    like_target(db, 'post', target_id)
    return success(like_state(db, 'post', target_id, user.id if user else None))


@router.put('/forum/posts/{target_id}/like', response_model=ApiResponse[LikeState])
def add_post_like(target_id: int, db: DatabaseSession, user: CurrentUser):
    return success(set_like(db, 'post', target_id, user, True))


@router.delete('/forum/posts/{target_id}/like', response_model=ApiResponse[LikeState])
def remove_post_like(target_id: int, db: DatabaseSession, user: CurrentUser):
    return success(set_like(db, 'post', target_id, user, False))


@router.get('/notifications/unread-count', response_model=ApiResponse[dict])
def count_unread(db: DatabaseSession, user: CurrentUser):
    return success({'count': unread_count(db, user.id)})


@router.get('/notifications', response_model=ApiResponse[NotificationPage])
def inbox(db: DatabaseSession, user: CurrentUser, unread_only: bool = False,
          page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    filters = [Notification.recipient_id == user.id]
    if unread_only:
        filters.append(Notification.is_read.is_(False))
    total = db.scalar(select(func.count()).select_from(Notification).where(*filters))
    items = db.scalars(select(Notification).where(*filters).order_by(Notification.id.desc())
        .offset((page - 1) * page_size).limit(page_size)).all()
    return success(dict(items=[read_notification(db, item) for item in items], total=total,
                        page=page, page_size=page_size, unread_count=unread_count(db, user.id)))


@router.patch('/notifications/read-all', response_model=ApiResponse[None])
def mark_all(payload: ReadAll, db: DatabaseSession, user: CurrentUser):
    db.execute(update(Notification).where(Notification.recipient_id == user.id,
        Notification.id <= payload.up_to_id, Notification.is_read.is_(False)).values(is_read=True))
    db.commit()
    return success(None)


@router.patch('/notifications/{notification_id}/read', response_model=ApiResponse[None])
def mark_read(notification_id: int, db: DatabaseSession, user: CurrentUser):
    item = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.recipient_id == user.id))
    if item is None:
        raise AppError(404, '消息不存在')
    item.is_read = True
    db.commit()
    return success(None)
