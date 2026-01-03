from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.database import get_session
from app.schemas.accounts import AccountBase, AccountUpdate, Account as AccountResponse
from app.schemas.transactions import TransactionResponse
import app.crud.accounts as account_crud
from app.utils.dependencies import get_current_user
import datetime
import app.utils.datetime as date_utils
from collections.abc import Sequence
from typing import Annotated
from app.models import Transaction, User
import app.utils.messages as messages
import app.utils.exceptions as err

router: APIRouter = APIRouter()


@router.get(path="", response_model=list[AccountResponse])
async def get_all_accounts(
    token: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    # TODO: lock this endpoint to user accounts only
    accounts = account_crud.get_all_accounts(session)
    return accounts


@router.get(
   path="/{account_id}", response_model=AccountResponse
)
async def get_account_by_id(
    user: Annotated[str, Depends(get_current_user)],
    account_id: int,
    session: Session = Depends(get_session),
):
    account = account_crud.get_account_by_id(account_id, user, session)
    return account


@router.post(path="", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account_endpoint(
    account_data: AccountBase,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    new_account = account_crud.create_account(account_data, user, session)
    return new_account


@router.patch(
    path="/{account_id}", status_code=status.HTTP_200_OK, response_model=AccountResponse
)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    user: Annotated[str, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    account = account_crud.update_account(account_id, account_data, user, session)
    return account


# TODO: This endpoint will need pagination!
@router.get(
    path="/{account_id}/transactions",
    status_code=status.HTTP_200_OK,
    response_model=Sequence[TransactionResponse],
)
async def get_account_transactions(
    account_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
) -> Sequence[Transaction]:
    # Fail the request when one of the date ranges is set
    # and the other isnt
    if (not from_date and to_date) or (from_date and not to_date):
        raise err.BadRequestException(message=messages.REQUIRED_DATE_RANGE)
    start_date: datetime.date = from_date or date_utils.first_day_of_month()
    end_date: datetime.date = to_date or date_utils.last_day_of_month()
    transactions: Sequence[Transaction] = account_crud.get_account_transactions(
        user.id, account_id, start_date, end_date, session
    )
    return transactions
