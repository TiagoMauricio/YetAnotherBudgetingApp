from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.schemas.users import User as UserResponse
from app.schemas.accounts import Account as AccountSchema

# import app.crud.users as user_crud
import app.crud.accounts as acc_crud
from typing import Annotated
from app.models import User, Account
from collections.abc import Sequence
from app.utils.dependencies import get_current_user
from app.utils import exceptions as err
from app.utils import messages

router: APIRouter = APIRouter()


@router.get(path="", response_model=list[UserResponse])
async def get_all_users(
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Sequence[User] | None:
    """Fetch all users"""

    # users: Sequence[User] = user_crud.find_all_users(session)
    return []


@router.get(path="/{user_id}/accounts", response_model=list[AccountSchema])
async def get_user_accounts(
    user_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> Sequence[Account]:
    """Get user accounts"""

    if not user_id == user.id:
        raise err.OperationNotPermitedException(message=messages.RESOURCE_ACCESS_DENIED)
    accounts: Sequence[Account] = acc_crud.get_user_owned_accounts(
        user_id=user_id, session=session
    )
    return accounts
