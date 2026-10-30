from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class ProductLike(Base):
    __tablename__ = 'product_likes'
    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='uq_product_like_user'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), index=True)


class PostLike(Base):
    __tablename__ = 'post_likes'
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='uq_post_like_user'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('forum_posts.id', ondelete='CASCADE'), index=True)


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = (Index('ix_notifications_inbox', 'recipient_id', 'is_read', 'id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    event_key: Mapped[str] = mapped_column(String(160), unique=True)
    kind: Mapped[str] = mapped_column(String(40))
    message: Mapped[str] = mapped_column(String(350))
    target_type: Mapped[str] = mapped_column(String(20))
    target_id: Mapped[int] = mapped_column()
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
