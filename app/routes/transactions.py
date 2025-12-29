from venv import create
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from starlette import status
from app.database import get_session
from app.utils.dependencies import get_current_user
from app.schemas.transactions import TransactionResponse, TransactionUpdate
from app.crud import transactions as t_crud, accounts as acc_crud

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
) -> TransactionResponse | None:
    transaction: TransactionResponse | None = t_crud.find_transaction_by_id(
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
    transaction_data: TransactionResponse,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> TransactionResponse:
    transaction: TransactionResponse = t_crud.create_transaction(
        transaction_data, user, session
    )
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_data: TransactionUpdate,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> TransactionResponse:
    transaction: TransactionResponse | None = t_crud.update_transaction(transaction_data, user, session)
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
    return transaction


@router.delete("/{transaction_id")
async def delete_transaction():
    pass


@router.get("", response_model=list[TransactionResponse])
async def get_account_transactions():
    pass
