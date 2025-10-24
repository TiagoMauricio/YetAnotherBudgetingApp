from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)}
    )
    is_active: bool = Field(default=True, sa_column_kwargs={"server_default": "1"})
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class Entry(SQLModel, table=True):
    id: int = Field(primary_key=True)
    account_id: int = Field(foreign_key="account.id", nullable=False)
    category_id: Optional[int] = Field(foreign_key="category.id")
    user_id: Optional[int] = Field(foreign_key="user.id")
    type: str = Field(regex="^(income|expense)$")
    amount: float
    description: Optional[str] = None
    entry_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")
    name: str
    type: str = Field(regex="^(income|expense)$")
    is_default: bool = Field(default=False)


class Account(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True, nullable=False)
    currency_code: str = Field(foreign_key="currency.code", nullable=False)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AccountMembership(SQLModel, table=True):
    account_id: int = Field(foreign_key="account.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="member")
    is_owner: bool = Field(default=False)
    joined_at: datetime = Field(default_factory=datetime.now)


class Currency(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    symbol: str
    is_active: bool = Field(default=True)
