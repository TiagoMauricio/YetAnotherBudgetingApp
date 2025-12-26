from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from starlette.status import HTTP_200_OK
from app.database import get_session
from app.schemas.accounts import AccountBase, AccountUpdate, Account as AccountResponse
import app.crud.accounts as account_crud
from app.utils.dependencies import get_current_user

from typing import Annotated

router = APIRouter()


@router.get("", response_model=list[AccountResponse])
async def get_all_accounts(token: Annotated[str, Depends(get_current_user)], session: Session = Depends(get_session)):
    accounts = account_crud.get_all_accounts(session)
    return accounts


@router.get("/{account_id}", status_code=HTTP_200_OK, response_model=AccountResponse)
async def get_account_by_id(user: Annotated[str, Depends(get_current_user)], account_id: int, session: Session = Depends(get_session)):
    account = account_crud.get_account_by_id(account_id, user, session)
    return account


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account_endpoint(
    account_data: AccountBase,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    new_account = account_crud.create_account(account_data, user, session)
    return new_account


@router.patch(path="/{account_id}", status_code=HTTP_200_OK, response_model=AccountResponse)
async def update_account(
        account_id: int,
        account_data: AccountUpdate,
        user: Annotated[str, Depends(get_current_user)],
        session: Session = Depends(get_session)):
    account = account_crud.update_account(account_id, account_data, user, session)
    return account
