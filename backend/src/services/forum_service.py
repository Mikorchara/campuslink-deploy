from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from src.core.exceptions import AppError
from src.models.forum import ForumComment, ForumPost
from src.schemas.forum import CommentRead, PostRead
from src.schemas.user import SellerInfo
from src.services.product_service import _relative_time


def get_post(db: Session, post_id: int, *, lock: bool = False) -> ForumPost:
    query = select(ForumPost).options(selectinload(ForumPost.author)).where(ForumPost.id == post_id)
    if lock:
        query = query.with_for_update()
    post = db.scalar(query)
    if post is None:
        raise AppError(404, "帖子不存在或已删除")
    return post


def ensure_owner(author_id: int, user_id: int) -> None:
    if author_id != user_id:
        raise AppError(403, "只能管理自己发布的内容")


def read_post(db: Session, post: ForumPost, comment_count: int | None = None) -> PostRead:
    if comment_count is None:
        comment_count = db.scalar(select(func.count()).select_from(ForumComment).where(ForumComment.post_id == post.id))
    return PostRead(
        id=post.id, title=post.title, content=post.content, summary=" ".join(post.content.split())[:160],
        category=post.category, tag=post.category, tagType="green" if post.category in {"学习", "备考"} else "blue",
        image_url=post.image_url, author=SellerInfo(id=post.author.id, name=post.author.username, avatar=post.author.avatar),
        comment_count=comment_count, created_at=post.created_at, updated_at=post.updated_at,
        created_date=_relative_time(post.created_at),
    )


def list_posts(db: Session, *, page: int, page_size: int, keyword: str | None = None,
               category: str | None = None, author_id: int | None = None) -> dict:
    filters = []
    if keyword and keyword.strip():
        # Escape wildcard characters so a keyword is a literal substring.
        escaped = keyword.strip().replace("/", "//").replace("%", "/%").replace("_", "/_")
        filters.append(or_(ForumPost.title.ilike(f"%{escaped}%", escape="/"), ForumPost.content.ilike(f"%{escaped}%", escape="/")))
    if category:
        filters.append(ForumPost.category == category)
    if author_id is not None:
        filters.append(ForumPost.author_id == author_id)
    total = db.scalar(select(func.count()).select_from(ForumPost).where(*filters))
    counts = select(ForumComment.post_id, func.count().label("n")).group_by(ForumComment.post_id).subquery()
    rows = db.execute(select(ForumPost, func.coalesce(counts.c.n, 0))
        .outerjoin(counts, counts.c.post_id == ForumPost.id).options(selectinload(ForumPost.author))
        .where(*filters).order_by(ForumPost.created_at.desc(), ForumPost.id.desc())
        .offset((page - 1) * page_size).limit(page_size)).all()
    return dict(items=[read_post(db, post, count) for post, count in rows], total=total, page=page, page_size=page_size)


def read_comment(comment: ForumComment) -> CommentRead:
    return CommentRead(id=comment.id, post_id=comment.post_id, content=comment.content,
        author=SellerInfo(id=comment.author.id, name=comment.author.username, avatar=comment.author.avatar),
        created_at=comment.created_at, updated_at=comment.updated_at)
