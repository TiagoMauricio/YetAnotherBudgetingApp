from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field


class AccountMembership(SQLModel, table=True):
    account_id: UUID = Field(foreign_key="account.id", primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="member")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
