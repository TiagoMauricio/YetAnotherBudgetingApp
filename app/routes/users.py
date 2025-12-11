from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.schemas.users import User as UserResponse
import app.crud.users as user_crud
from typing import Annotated

from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def get_all_users(token: Annotated[str,Depends(get_current_user)], session: Session = Depends(get_session)):
    """Fetch all users"""

    users = user_crud.find_all_users(session)
    return users
