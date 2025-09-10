from datetime import datetime
from typing import List
from pydantic import BaseModel, UUID4
from .user import UserOut


class AccountBase(BaseModel):
    pass


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    pass


class AccountOut(AccountBase):
    id: UUID4
    created_at: datetime
    users: List[UserOut] = []

    class Config:
        from_attributes = True
