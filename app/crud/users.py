from sqlmodel import Session, select
from app.models import User
from app.schemas import UserCreate
from app.utils.security import hash_password

def find_user_by_email(email: str, session: Session):
    database_query = select(User).where(User.email == email)
    user = session.exec(database_query).first()
    return user

def create_user(user: UserCreate, session: Session):
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def find_all_users(session: Session):
    database_query = select(User)
    users = session.exec(database_query).all()
    return users
