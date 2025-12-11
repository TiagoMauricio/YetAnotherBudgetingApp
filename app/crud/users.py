from sqlmodel import Session, select
from app.database import get_session
from app.models import User
from app.schemas.users import UserCreate
from app.utils.security import hash_password
from fastapi import Depends, HTTPException


def find_user_by_email(email: str, session: Session):
    database_query = select(User).where(User.email == email and User.is_active)
    user = session.exec(database_query).first()
    return user


def find_user_by_id(user_id: int, session: Session):
    return session.get(User, user_id)


def create_user(user: UserCreate, session: Session):
    new_user = User(
        email=user.email, name=user.name, password_hash=hash_password(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


def find_all_users(session: Session):
    database_query = select(User)
    users = session.exec(database_query).all()
    return users


def update_user(user_id: int, user_data: UserCreate, session: Session):
    user = find_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_data.name
    if user_data.password:
        user.password_hash = hash_password(user_data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
