from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from uuid import uuid4
from app.database import get_session
from app.models import User
from app.schemas import UserCreate, User as UserResponse
from typing import List
from app.crud.users import create_user, find_user_by_email, find_all_users

router = APIRouter()

@router.post("/users", response_model=UserResponse)
async def create_user_endpoint(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Create a new user"""

    # Check if user with this email already exists
    existing_user = find_user_by_email(user_data.email, session)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    # Create new user
    new_user = create_user(user_data, session)
    return new_user

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    session: Session = Depends(get_session)
):
    """Fetch all users"""

    users = find_all_users(session)
    return users
