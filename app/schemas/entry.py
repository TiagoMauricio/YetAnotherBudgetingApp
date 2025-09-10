from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID4


class EntryBase(BaseModel):
    account_id: UUID4
    category_id: Optional[UUID4] = None
    type: str = Field(pattern="^(income|expense)$")
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", max_length=3, min_length=3)
    description: Optional[str] = None
    entry_date: date


class EntryCreate(EntryBase):
    pass


class EntryUpdate(BaseModel):
    category_id: Optional[UUID4] = None
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3, min_length=3)
    description: Optional[str] = None
    entry_date: Optional[date] = None


class EntryOut(EntryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
