from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    name: None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class User(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: int
    created_at: datetime
    updated_at: datetime

#    class Config:
#        from_attributes = True


# Account Schemas
class AccountBase(BaseModel):
    """Base account schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Account name")
    currency_code: str = Field(..., min_length=3, max_length=3, description="3-letter currency code (e.g., USD, EUR)")
    description: Optional[str] = Field(None, max_length=500, description="Optional account description")


class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    pass


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Account name")
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3, description="3-letter currency code")
    description: Optional[str] = Field(None, max_length=500, description="Account description")


class Account(AccountBase):
    """Schema for account response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountMember(BaseModel):
    """Schema for account member information"""
    user_id: int
    email: str
    name: Optional[str]
    role: str
    is_owner: bool
    joined_at: datetime


class AccountMembershipCreate(BaseModel):
    """Schema for adding a user to an account"""
    user_id: int
    role: str = Field(default="member", description="Role of the user in the account")


class AccountWithMembers(Account):
    """Schema for account with member information"""
    members: list[AccountMember] = []
