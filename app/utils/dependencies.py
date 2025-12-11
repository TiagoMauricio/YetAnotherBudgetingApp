from fastapi import Depends
from sqlmodel import Session
from app.crud.users import find_user_by_email
from app.database import get_session
from app.utils.security import oauth2_scheme, verify_token
from app.models import User

def get_current_user(token: str = Depends(dependency=oauth2_scheme), session: Session = Depends(get_session)) -> User | None:
    token_data = verify_token(token)
    user_email: str = token_data['sub']
    user: User | None = find_user_by_email(email=user_email, session=session)
    return user
