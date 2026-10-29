from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.security import hash_password
from src.database.base import Base
from src.database.session import engine
from src.models import Product, User


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)) is not None:
        return

    users = [
        User(
            username="数学小佬",
            email="math@example.com",
            password_hash=hash_password("123456"),
            avatar="/assets/avatars/avatar_math.png",
            contact="QQ 102301520",
            bio="福州大学数学与统计学院",
        ),
        User(
            username="青柠",
            email="lime@example.com",
            password_hash=hash_password("123456"),
            avatar="/assets/avatars/avatar_lime.png",
            contact="微信 lime_fzu",
            bio="福州大学计算机与大数据学院",
        ),
        User(
            username="喵同学",
            email="cat@example.com",
            password_hash=hash_password("123456"),
            avatar="/assets/avatars/avatar_cat.png",
            contact="QQ 102301521",
            bio="福州大学旗山校区学生",
        ),
        User(
            username="数码学长",
            email="digital@example.com",
            password_hash=hash_password("123456"),
            avatar="/assets/avatars/avatar_fzu_daily.png",
            contact="微信 digital_fzu",
        ),
        User(
            username="上岸小锦鲤",
            email="taro@example.com",
            password_hash=hash_password("123456"),
            avatar="/assets/avatars/avatar_taro.png",
            contact="QQ 102301522",
        ),
    ]
    db.add_all(users)
    db.flush()

    products = [
        Product(
            seller_id=users[0].id,
            title="高等数学（第七版）教材",
            description="福大生工大一自用教材，九成新，笔记清晰工整。",
            price=Decimal("15.00"),
            category="教材",
            image_url="/assets/images/goods_math_book.png",
            location="福州大学旗山校区生活一区",
        ),
        Product(
            seller_id=users[1].id,
            title="AirPods 3 自用出",
            description="官网正品国行，功能全部完好，送保护套。",
            price=Decimal("450.00"),
            category="数码",
            image_url="/assets/images/goods_airpods.png",
            location="福州大学旗山校区风雨操场",
        ),
        Product(
            seller_id=users[2].id,
            title="护眼台灯 9成新",
            description="宿舍自用护眼台灯，无频闪，三档色温调节。",
            price=Decimal("60.00"),
            category="生活用品",
            image_url="/assets/images/goods_desk_lamp.png",
            location="福州大学旗山校区宿舍三区",
        ),
        Product(
            seller_id=users[3].id,
            title="iPad Air 5 64G 星光色",
            description="原装箱说全，无划痕，送磁吸保护套。",
            price=Decimal("2999.00"),
            category="数码",
            image_url="/assets/images/goods_airpods.png",
            location="福州大学图书馆一楼大厅",
        ),
        Product(
            seller_id=users[4].id,
            title="考研英语二历年真题详解",
            description="黄皮书全新未动笔，附赠核心词汇手册。",
            price=Decimal("25.00"),
            category="教材",
            image_url="/assets/images/goods_math_book.png",
            location="福州大学公共教学楼文科楼",
        ),
        Product(
            seller_id=users[2].id,
            title="美的宿舍静音小风扇",
            description="四档风速，USB 充电，轻便好携带。",
            price=Decimal("28.00"),
            category="生活用品",
            image_url="/assets/images/goods_desk_lamp.png",
            location="福州大学生活二区菜鸟驿站",
        ),
    ]
    db.add_all(products)
    db.commit()

