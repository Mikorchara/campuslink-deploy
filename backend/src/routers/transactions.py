from fastapi import APIRouter, status

from src.dependencies.auth import CurrentUser, DatabaseSession
from src.schemas.common import ApiResponse, success
from src.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionStatusUpdate,
)
from src.services.transaction_service import (
    create_transaction,
    list_transactions,
    serialize_transaction,
    update_transaction_status,
)


router = APIRouter(tags=["Transactions"])


@router.get("/transactions", response_model=ApiResponse[list[TransactionRead]])
def get_transactions(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[list[TransactionRead]]:
    return success(
        [serialize_transaction(item) for item in list_transactions(db, current_user)]
    )


@router.post(
    "/products/{product_id}/transactions",
    response_model=ApiResponse[TransactionRead],
    status_code=status.HTTP_201_CREATED,
)
def request_transaction(
    product_id: int,
    payload: TransactionCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[TransactionRead]:
    item = create_transaction(db, current_user, product_id, payload)
    return success(serialize_transaction(item), message="交易请求已发送", code=201)


@router.patch(
    "/transactions/{transaction_id}",
    response_model=ApiResponse[TransactionRead],
)
def change_transaction_status(
    transaction_id: int,
    payload: TransactionStatusUpdate,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> ApiResponse[TransactionRead]:
    item = update_transaction_status(
        db, current_user, transaction_id, payload.status
    )
    return success(serialize_transaction(item), message="交易状态已更新")

