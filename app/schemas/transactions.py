from pydantic import BaseModel
from datetime import datetime


class BaseTransaction(BaseModel):
    """Base schema for transacitons"""

    category_id: int
    type: str
    amount: float
    description: str
    date: datetime


class TransactionResponse(BaseTransaction):
    """Base schema for transaction responses"""

    account_id: int

