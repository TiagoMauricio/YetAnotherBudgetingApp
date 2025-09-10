from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from app.models import AccountMembership, Account, Entry


class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str = Field(nullable=False)
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    memberships: List["Account"] = Relationship(
        back_populates="members", link_model=AccountMembership
    )
    entries: List["Entry"] = Relationship(back_populates="creator")
