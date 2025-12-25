from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import ClassVar


# Account Schemas
class AccountBase(BaseModel):
    """Base account schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Account name")
    currency_code: str = Field(..., min_length=3, max_length=3, description="3-letter currency code (e.g., USD, EUR)")
    description: str | None = Field(None, max_length=500, description="Optional account description")


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    currency_code: str | None = Field(None, min_length=3, max_length=3, description="3-letter currency code")
    description: str | None = Field(None, max_length=500, description="Account description")


class Account(AccountBase):
    """Schema for account response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class AccountMember(BaseModel):
    """Schema for account member information"""
    user_id: int
    email: str
    name: str | None
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
