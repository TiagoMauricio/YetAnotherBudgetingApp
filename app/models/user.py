from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.entry import Entry


class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    memberships: List["Account"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={"secondary": "accountmembership"},
    )
    entries: List["Entry"] = Relationship(back_populates="creator")
