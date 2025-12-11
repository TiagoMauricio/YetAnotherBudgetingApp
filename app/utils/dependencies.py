from fastapi import Depends
from app.utils.security import oauth2_scheme, verify_token

def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
