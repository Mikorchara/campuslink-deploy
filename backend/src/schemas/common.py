from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T


def success(data: T, message: str = "success", code: int = 200) -> ApiResponse[T]:
    return ApiResponse(code=code, message=message, data=data)

