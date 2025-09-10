from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.entry import Entry
    from app.models.account import Account


class Category(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    account_id: Optional[UUID] = Field(default=None, foreign_key="account.id")
    name: str
    type: str = Field(regex="^(income|expense)$")
    is_default: bool = Field(default=False)

    account: Optional["Account"] = Relationship(back_populates="categories")
    entries: List["Entry"] = Relationship(back_populates="category")
