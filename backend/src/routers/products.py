from fastapi import APIRouter, Query, status as http_status

from src.dependencies.auth import CurrentUser, DatabaseSession
from src.models.product import ProductStatus
from src.schemas.common import ApiResponse, success
from src.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductStatusUpdate,
    ProductUpdate,
)
from src.schemas.user import SellerContact
from src.services.product_service import (
    create_product,
    delete_product,
    get_product,
    list_products,
    serialize_product,
    set_product_status,
    update_product,
)
from src.services.user_service import serialize_contact


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ApiResponse[list[ProductRead]])
def get_products(
    db: DatabaseSession,
    keyword: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=50),
    status: ProductStatus | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse[list[ProductRead]]:
    products = list_products(
        db,
        keyword=keyword,
        category=category,
        status=status,
        page=page,
        page_size=page_size,
    )
    return success([serialize_product(item) for item in products])


@router.get("/{product_id}", response_model=ApiResponse[ProductRead])
def get_product_detail(
    product_id: int,
    db: DatabaseSession,
) -> ApiResponse[ProductRead]:
    return success(serialize_product(get_product(db, product_id)))


@router.post(
    "",
    response_model=ApiResponse[ProductRead],
    status_code=http_status.HTTP_201_CREATED,
)
def publish_product(
    payload: ProductCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[ProductRead]:
    product = create_product(db, current_user, payload)
    return success(serialize_product(product), message="商品发布成功", code=201)


@router.put("/{product_id}", response_model=ApiResponse[ProductRead])
def edit_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[ProductRead]:
    product = update_product(db, product_id, current_user, payload)
    return success(serialize_product(product), message="商品信息已更新")


@router.patch("/{product_id}/status", response_model=ApiResponse[ProductRead])
def edit_product_status(
    product_id: int,
    payload: ProductStatusUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[ProductRead]:
    product = set_product_status(db, product_id, current_user, payload.status)
    return success(serialize_product(product), message="商品状态已更新")


@router.delete("/{product_id}", response_model=ApiResponse[None])
def remove_product(
    product_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[None]:
    delete_product(db, product_id, current_user)
    return success(None, message="商品已删除")


@router.get("/{product_id}/contact", response_model=ApiResponse[SellerContact])
def get_seller_contact(
    product_id: int,
    _current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[SellerContact]:
    product = get_product(db, product_id)
    return success(serialize_contact(product.seller))

