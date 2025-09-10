from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
) -> List[User]:
    """Get all users with optional filtering."""
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_superuser is not None:
        query = query.filter(User.is_superuser == is_superuser)
    return query.offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user_in.password)
    is_superuser_value = bool(user_in.is_superuser) if user_in.is_superuser is not None else False  # noqa: E501
    is_active_value = bool(user_in.is_active) if user_in.is_active is not None else True  # noqa: WPS425,E501
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=is_active_value,
        is_superuser=is_superuser_value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update a user."""
    user_data = user_in.dict(exclude_unset=True)
    if "password" in user_data and user_in.password:
        db_user.hashed_password = get_password_hash(user_in.password)
    update_data = user_in.dict(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_accounts(db: Session, user_id: UUID) -> List[dict]:
    """Get all accounts for a user with membership details."""
    user = get_user(db, user_id=user_id)
    if not user:
        return []
    return [
        {
            "id": membership.account.id,
            "name": membership.account.name,
            "description": membership.account.description,
            "balance": membership.account.balance,
            "currency": membership.account.currency,
            "is_active": membership.account.is_active,
            "created_at": membership.account.created_at,
            "updated_at": membership.account.updated_at,
            "role": membership.role,
            "joined_at": membership.joined_at,
        }
        for membership in user.account_memberships
    ]
