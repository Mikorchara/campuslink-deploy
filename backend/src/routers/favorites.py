from fastapi import APIRouter, status

from src.dependencies.auth import CurrentUser, DatabaseSession
from src.schemas.common import ApiResponse, success
from src.schemas.favorite import FavoriteRead, FavoriteState
from src.services.favorite_service import (
    add_favorite,
    is_favorited,
    list_favorites,
    remove_favorite,
)


router = APIRouter(tags=["Favorites"])


@router.get("/favorites", response_model=ApiResponse[list[FavoriteRead]])
def get_favorites(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[list[FavoriteRead]]:
    return success(list_favorites(db, current_user))


@router.get(
    "/products/{product_id}/favorite",
    response_model=ApiResponse[FavoriteState],
)
def get_favorite_state(
    product_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[FavoriteState]:
    return success(
        FavoriteState(
            product_id=product_id,
            is_favorited=is_favorited(db, current_user, product_id),
        )
    )


@router.post(
    "/products/{product_id}/favorite",
    response_model=ApiResponse[FavoriteState],
    status_code=status.HTTP_201_CREATED,
)
def create_favorite(
    product_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[FavoriteState]:
    add_favorite(db, current_user, product_id)
    return success(
        FavoriteState(product_id=product_id, is_favorited=True),
        message="收藏成功",
        code=201,
    )


@router.delete(
    "/products/{product_id}/favorite",
    response_model=ApiResponse[FavoriteState],
)
def delete_favorite(
    product_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[FavoriteState]:
    remove_favorite(db, current_user, product_id)
    return success(
        FavoriteState(product_id=product_id, is_favorited=False),
        message="已取消收藏",
    )

