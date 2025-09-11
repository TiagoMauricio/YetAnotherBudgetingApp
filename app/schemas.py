from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class User(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
