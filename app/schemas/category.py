from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID4


class CategoryBase(BaseModel):
    name: str
    type: str = Field(pattern="^(income|expense)$")
    is_default: bool = False
    account_id: Optional[UUID4] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    is_default: Optional[bool] = None


class CategoryOut(CategoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
