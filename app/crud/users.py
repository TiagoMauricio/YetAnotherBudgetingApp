from sqlmodel import Session, select

from app.models import User
from app.schemas.users import UserCreate, UserUpdate
from app.utils.exceptions import exceptions as err
from app.utils.security import hash_password


def find_user_by_email(email: str, session: Session):
    database_query = select(User).where(User.email == email, User.is_active == True)
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


def update_user(user: User, user_data: UserUpdate, session: Session) -> User:
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def deactivate_user(user: User, session: Session) -> None:
    user.is_active = False
    session.add(user)
    session.commit()
