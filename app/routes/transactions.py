from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status

from app.crud import accounts as acc_crud
from app.crud import transactions as t_crud
from app.database import get_session
from app.models import Transaction
from app.schemas.transactions import (
    BaseTransaction,
    TransactionResponse,
    TransactionUpdate,
)
from app.utils.dependencies import get_current_user
from app.utils.exceptions import exceptions as err

router = APIRouter(tags=["transactions"])


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_transaction(
    transaction_id: int,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Transaction | None:
    try:
        transaction: Transaction | None = t_crud.find_transaction_by_id(
            transaction_id, session
        )
    except Exception as e:
        raise err.UnknownException("Something unexpected happened.") from e

    # TODO: change responsibility of throwing errors
    # to crud function
    if not transaction:
        raise err.EntityNotFoundException("Transaction does not exist.")
    elif not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise err.NotPermitedException("You do not have access to this account.")
    return transaction


@router.post(
    "", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: BaseTransaction,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Transaction:
    transaction: Transaction = t_crud.create_transaction(
        transaction_data, user, session
    )
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Transaction | None:
    transaction: Transaction | None = t_crud.find_transaction_by_id(
        transaction_id, session
    )
    if not transaction:
        raise err.EntityNotFoundException("Transaction not found")
    if not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise err.EntityNotFoundException("User does not have acccess to account.")
    updated_transaction: Transaction | None = t_crud.update_transaction(
        transaction_id, transaction_data, session
    )
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    transaction: Transaction | None = t_crud.find_transaction_by_id(
        transaction_id, session
    )
    if not transaction:
        raise err.EntityNotFoundException("Transaction not found")
    if not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise err.NotPermitedException("User does not have acccess to account.")
    deleted_transaction: bool = t_crud.delete_transaction(transaction_id, session)
    if not deleted_transaction:
        raise err.UnknownException(
            "Something went wrong while trying to delete transaction."
        )
