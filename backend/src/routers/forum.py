from fastapi import APIRouter, Query
from uuid import uuid4
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.core.exceptions import AppError
from src.dependencies.auth import CurrentUser, DatabaseSession
from src.models.forum import ForumComment, ForumPost
from src.schemas.common import ApiResponse, success
from src.schemas.forum import CommentPage, CommentRead, CommentWrite, ForumCategory, PostPage, PostRead, PostWrite
from src.services.forum_service import ensure_owner, get_post, list_posts, read_comment, read_post
from src.services.activity_service import notify
from src.services.forum_service import list_participated_posts

router = APIRouter(prefix="/forum", tags=["Forum"])


@router.get("/posts", response_model=ApiResponse[PostPage])
def posts(db: DatabaseSession, keyword: str | None = Query(None, max_length=120),
          category: ForumCategory | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return success(list_posts(db, keyword=keyword, category=category, page=page, page_size=page_size))


@router.get("/posts/mine", response_model=ApiResponse[PostPage])
def my_posts(db: DatabaseSession, user: CurrentUser, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return success(list_posts(db, author_id=user.id, page=page, page_size=page_size))


@router.post("/posts", response_model=ApiResponse[PostRead], status_code=201)
def create_post(payload: PostWrite, db: DatabaseSession, user: CurrentUser):
    post = ForumPost(author_id=user.id, **payload.model_dump())
    db.add(post)
    db.commit()
    return success(read_post(db, get_post(db, post.id)), code=201, message="帖子发布成功")


@router.get('/posts/participated', response_model=ApiResponse[PostPage])
def participated_posts(db: DatabaseSession, user: CurrentUser,
                       page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return success(list_participated_posts(db, user.id, page=page, page_size=page_size))


@router.get("/posts/{post_id}", response_model=ApiResponse[PostRead])
def post_detail(post_id: int, db: DatabaseSession):
    return success(read_post(db, get_post(db, post_id)))


@router.put("/posts/{post_id}", response_model=ApiResponse[PostRead])
def update_post(post_id: int, payload: PostWrite, db: DatabaseSession, user: CurrentUser):
    post = get_post(db, post_id, lock=True)
    ensure_owner(post.author_id, user.id)
    for key, value in payload.model_dump().items():
        setattr(post, key, value)
    db.commit()
    return success(read_post(db, post), message="帖子已更新")


@router.delete("/posts/{post_id}", response_model=ApiResponse[None])
def delete_post(post_id: int, db: DatabaseSession, user: CurrentUser):
    post = get_post(db, post_id, lock=True)
    ensure_owner(post.author_id, user.id)
    db.delete(post)
    db.commit()
    return success(None, message="帖子及其评论已删除")


@router.get("/posts/{post_id}/comments", response_model=ApiResponse[CommentPage])
def comments(post_id: int, db: DatabaseSession, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    get_post(db, post_id)
    query = select(ForumComment).where(ForumComment.post_id == post_id)
    total = db.scalar(select(func.count()).select_from(ForumComment).where(ForumComment.post_id == post_id))
    items = db.scalars(query.options(selectinload(ForumComment.author)).order_by(ForumComment.created_at, ForumComment.id)
                       .offset((page - 1) * page_size).limit(page_size)).all()
    return success(dict(items=[read_comment(item) for item in items], total=total, page=page, page_size=page_size))


@router.post("/posts/{post_id}/comments", response_model=ApiResponse[CommentRead], status_code=201)
def create_comment(post_id: int, payload: CommentWrite, db: DatabaseSession, user: CurrentUser):
    post = get_post(db, post_id, lock=True)  # Coordinate with concurrent post deletion.
    comment = ForumComment(post_id=post_id, author_id=user.id, **payload.model_dump())
    db.add(comment)
    db.flush()
    notify(db, recipient_id=post.author_id, actor_id=user.id, event_key=f'comment:{uuid4().hex}',
        kind='post_comment', message=f'{user.username} 评论了你的帖子《{post.title}》',
        target_type='post', target_id=post.id)
    db.commit()
    return success(read_comment(comment), code=201, message="评论已发布")


def owned_comment(db, comment_id, user):
    comment = db.scalar(select(ForumComment).where(ForumComment.id == comment_id).with_for_update())
    if comment is None:
        raise AppError(404, "评论不存在或已删除")
    ensure_owner(comment.author_id, user.id)
    return comment


@router.put("/comments/{comment_id}", response_model=ApiResponse[CommentRead])
def update_comment(comment_id: int, payload: CommentWrite, db: DatabaseSession, user: CurrentUser):
    comment = owned_comment(db, comment_id, user)
    comment.content = payload.content
    db.commit()
    return success(read_comment(comment), message="评论已更新")


@router.delete("/comments/{comment_id}", response_model=ApiResponse[None])
def delete_comment(comment_id: int, db: DatabaseSession, user: CurrentUser):
    db.delete(owned_comment(db, comment_id, user))
    db.commit()
    return success(None, message="评论已删除")
