from fastapi import APIRouter

from src.dependencies.auth import CurrentUser, DatabaseSession
from src.schemas.common import ApiResponse, success
from src.schemas.product import ProductRead
from src.schemas.user import UserRead, UserUpdate
from src.services.product_service import list_products, serialize_product
from src.services.user_service import serialize_user, update_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserRead])
def get_me(current_user: CurrentUser) -> ApiResponse[UserRead]:
    return success(serialize_user(current_user))


@router.put("/me", response_model=ApiResponse[UserRead])
def update_me(
    payload: UserUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[UserRead]:
    return success(
        serialize_user(update_user(db, current_user, payload)),
        message="用户信息已更新",
    )


@router.get("/me/products", response_model=ApiResponse[list[ProductRead]])
def get_my_products(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[list[ProductRead]]:
    products = list_products(
        db, seller_id=current_user.id, page=1, page_size=100
    )
    return success([serialize_product(item) for item in products])

