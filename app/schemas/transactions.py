from pydantic import BaseModel
from datetime import date


class BaseTransaction(BaseModel):
    """Base schema for transacitons"""

    account_id: int
    category_id: int
    type: str
    amount: float
    description: str
    date: date


class TransactionResponse(BaseTransaction):
    """Base schema for transaction responses"""

    id: int


