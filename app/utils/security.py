from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, select

import jwt
from fastapi import HTTPException, status
from argon2 import PasswordHasher, exceptions
from app.models import RefreshToken

from fastapi.security import OAuth2PasswordBearer

from app.config import settings

# Initialize Argon2 password hasher
ph = PasswordHasher(
    time_cost=3,  # Number of iterations
    memory_cost=65536,  # 64MB
    parallelism=4,  # Number of parallel threads
    hash_len=32,  # Hash length
    salt_len=16,  # Salt length
)

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')

def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash using Argon2"""
    try:
        return ph.verify(hashed_password, plain_password)
    except (exceptions.VerifyMismatchError, exceptions.InvalidHash):
        return False
    except exceptions.VerificationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during password verification",
        )


def create_access_token(data: dict[str, Any]) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """Verify JWT access token and return its payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )

        if payload.get("type") != "access":
            raise credentials_exception

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception


def create_refresh_token(data: dict[str, Any], user_id: int, db: Session) -> str:
    """Create a new JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(to_encode, settings.refresh_token_secret_key, algorithm=ALGORITHM)
    db.add(RefreshToken(token=token, user_id=user_id, expires_at=expire))
    db.commit()
    return token


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify refresh token and return its payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.refresh_token_secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )

        if payload.get("type") != "refresh":
            raise credentials_exception

        return payload
    except jwt.ExpiredSignatureError:
        revoke_refresh_token(token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception


def revoke_refresh_token(token: str, db: Session) -> None:
    """Revoke a refresh token by adding it to the database"""
    try:
        jwt.decode(
            token,
            settings.refresh_token_secret_key,
            algorithms=[ALGORITHM],
            options={"verify_exp": False},  # We want to revoke even if expired
        )
        # Check if token is already revoked
        statement = select(RefreshToken).where(
            RefreshToken.token == token
        )
        existing_token = db.exec(statement).first()

        if not existing_token:
            print("ERROR: Refresh token not found")
            return  # Token already revoked or doesn't exist

        # Mark token as revoked
        existing_token.revoked = True
        db.add(existing_token)
        db.commit()
        print("Refresh token revoked successfully")

    except jwt.PyJWTError:
        # TODO: LOG that an invalid token was provided
        print("ERROR: Invalid refresh token")
        pass
