from datetime import datetime, date
import enum
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional
from app.models import Account, Category, User


class Entry(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    account_id: UUID = Field(foreign_key="account.id", nullable=False)
    category_id: Optional[UUID] = Field(foreign_key="category.id")
    user_id: Optional[UUID] = Field(foreign_key="user.id")
    type: str = Field(regex="^(income|expense)$")
    amount: float
    currency: str = Field(default="USD")
    description: Optional[str] = None
    entry_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    account: Account = Relationship(back_populates="entries")
    category: Optional[Category] = Relationship(back_populates="entries")
    creator: Optional[User] = Relationship(back_populates="entries")
