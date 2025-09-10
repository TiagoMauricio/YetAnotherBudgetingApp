from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.entry import Entry
    from app.models.account_membership import AccountMembership


class Account(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    members: List["User"] = Relationship(
        back_populates="memberships",
        sa_relationship_kwargs={"secondary": "accountmembership"}
    )
    entries: List["Entry"] = Relationship(back_populates="account")
