from fastapi import APIRouter, status

from src.dependencies.auth import DatabaseSession
from src.schemas.auth import LoginData, LoginRequest, RegisterRequest
from src.schemas.common import ApiResponse, success
from src.schemas.user import UserRead
from src.services.auth_service import login_user, register_user
from src.services.user_service import serialize_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: DatabaseSession) -> ApiResponse[UserRead]:
    user = register_user(db, payload)
    return success(serialize_user(user), message="注册成功", code=201)


@router.post("/login", response_model=ApiResponse[LoginData])
def login(payload: LoginRequest, db: DatabaseSession) -> ApiResponse[LoginData]:
    return success(login_user(db, payload), message="登录成功")

