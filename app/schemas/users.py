from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class User(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: int
    created_at: datetime
    updated_at: datetime

#    class Config:
#
