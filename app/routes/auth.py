from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from typing import Annotated

from app.database import get_session
import app.crud.users as user_crud
from app.schemas.users import UserCreate, User as UserResponse
from app.schemas.token import Token, TokenRefresh
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
)

from app.utils.dependencies import get_current_user

router = APIRouter(tags=["authentication"])


def authenticate_user(email: str, password: str, session: Session):
    user = user_crud.find_user_by_email(email, session)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, session: Session = Depends(get_session)
) -> UserResponse:
    """Register a new user."""
    # Check if user with this email already exists
    existing_user = user_crud.find_user_by_email(user_data.email, session)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    # TODO: return 400 if password is not ok
    new_user = user_crud.create_user(user_data, session)

    # TODO: Send verification email

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests.

    - **username**: The user's email
    - **password**: The user's password
    """
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    user.last_login = datetime.now()
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email}, user_id=user.id, db=session)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    session: Session = Depends(get_session),
) -> Token:
    """Refresh an access token using a refresh token.

    - **refresh_token**: A valid refresh token
    """
    try:
        payload = verify_refresh_token(token_data.refresh_token)
        user_email = payload.get("sub")
        user = user_crud.find_user_by_email(email=user_email, session=session)
        revoke_refresh_token(token=token_data.refresh_token, db=session)
        access_token: str = create_access_token(data={"sub": user_email})
        refresh_token: str = create_refresh_token(data={"sub": user_email}, user_id=user.id, db=session)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except HTTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

@router.post("/logout")
async def logout(token: Annotated[str, Depends(get_current_user)], session: Session = Depends(get_session)):
    """
    Logout a user when a session is provided
    - **auth_token**: A valid authentication token
    """
    try:
        # TODO: how to actually logout the user?
        revoke_token(token, session)
    except HTTPException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
