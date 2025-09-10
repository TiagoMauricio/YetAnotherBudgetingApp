from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Relationship
from sqlmodel import SQLModel, Field
from app.models import Account, Entry


class Category(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    account_id: Optional[UUID] = Field(default=None, foreign_key="account.id")
    name: str
    type: str = Field(regex="^(income|expense)$")
    is_default: bool = Field(default=False)

    account: Optional[Account] = Relationship(back_populates="categories")
    entries: List["Entry"] = Relationship(back_populates="category")
