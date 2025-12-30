from pydantic import BaseModel
import datetime

class BaseTransaction(BaseModel):
    """Base schema for transacitons"""

    account_id: int
    category_id: int
    type: str
    amount: float
    description: str
    date: datetime.date


class TransactionResponse(BaseTransaction):
    """Base schema for transaction responses"""

    id: int

class TransactionUpdate(BaseModel):
    """Schema for transaction updates"""

    category_id: int | None = None
    type: str | None = None
    amount: float | None = None
    description: str | None = None
    # python was complaining that date by itself was a variable, idk why
    date: datetime.date | None = None
