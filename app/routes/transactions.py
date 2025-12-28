from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette import status
from app.database import get_session
from app.utils.dependencies import get_current_user
from app.schemas.transactions import TransactionResponse
import app.crud.transactions as t_crud

from typing import Annotated

router = APIRouter(tags=["transactions"])

@router.get("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
async def get_transaction(transaction_id: int, user: Annotated[str, Depends(get_current_user)], session: Session = Depends(get_session)) -> TransactionResponse | None:
    transaction: TransactionResponse | None = t_crud.find_transaction_by_id(transaction_id, session)
    return transaction


@router.post("", response_model=TransactionResponse)
async def create_transaction():
    pass


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction():
    pass


@router.delete("/{transaction_id")
async def delete_transaction():
    pass


@router.get("", response_model=list[TransactionResponse])
async def get_account_transactions():
    pass
