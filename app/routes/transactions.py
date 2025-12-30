from venv import create
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from starlette import status
from app.database import get_session
from app.utils.dependencies import get_current_user
from app.schemas.transactions import TransactionResponse, BaseTransaction
from app.crud import transactions as t_crud, accounts as acc_crud
from app.models import Transaction
from typing import Annotated

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
    transaction: Transaction | None = t_crud.find_transaction_by_id(
        transaction_id, session
    )
    # TODO: change responsibility of throwing errors
    # to crud function
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction does not exist."
        )
    elif not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this account.",
        )
    return transaction


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
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
    transaction_data: BaseTransaction,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Transaction | None:
    transaction: Transaction | None = t_crud.find_transaction_by_id(transaction_id, session)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    if not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have acccess to account."
        )
    updated_transaction: Transaction | None = t_crud.update_transaction(transaction_id, transaction_data, session)
    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int, user: Annotated[str, Depends(get_current_user)], session: Session = Depends(get_session)):
    transaction: Transaction | None = t_crud.find_transaction_by_id(transaction_id, session)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    if not acc_crud.user_has_account_access(user.id, transaction.account_id, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have acccess to account."
        )
    deleted_transaction: bool = t_crud.delete_transaction(transaction_id, session)
    if not deleted_transaction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while trying to delete transaction."
        )


