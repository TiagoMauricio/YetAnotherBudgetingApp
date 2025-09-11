from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Entry(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    account_id: UUID = Field(foreign_key="account.id", nullable=False)
    category_id: Optional[UUID] = Field(foreign_key="category.id")
    user_id: Optional[UUID] = Field(foreign_key="user.id")
    type: str = Field(regex="^(income|expense)$")
    amount: float
    currency: str = Field(default="USD")
    description: Optional[str] = None
    entry_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Category(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    account_id: Optional[UUID] = Field(default=None, foreign_key="account.id")
    name: str
    type: str = Field(regex="^(income|expense)$")
    is_default: bool = Field(default=False)

class Account(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AccountMembership(SQLModel, table=True):
    account_id: UUID = Field(foreign_key="account.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="member")
    joined_at: datetime = Field(default_factory=datetime.now)
