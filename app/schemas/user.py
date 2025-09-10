from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from .account import AccountOut


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserOut(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    memberships: List[AccountOut] = []

    class Config:
        from_attributes = True


class UserInDB(UserOut):
    password_hash: str
