from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

# import app.crud.users as user_crud
import app.crud.accounts as acc_crud
from app.database import get_session
from app.models import User
from app.schemas.accounts import AccountWithOwner as AccountSchema
from app.schemas.users import User as UserResponse
from app.utils import messages
from app.utils.dependencies import get_current_user
from app.utils.exceptions import exceptions as err

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
) -> list[dict]:
    """Get user accounts"""

    if not user_id == user.id:
        raise err.NotPermitedException(message=messages.RESOURCE_ACCESS_DENIED)
    rows = acc_crud.get_accounts_by_user_with_owner(user_id=user_id, session=session)
    return [{"owner": owner_id, **acc.model_dump()} for acc, owner_id in rows]
