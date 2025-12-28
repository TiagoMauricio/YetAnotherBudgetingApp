from pydantic import BaseModel
from datetime import datetime

class TransactionResponse(BaseModel):
    """Base schema for transactions"""
    account_id: int
    category_id: int
    type: str
    amount: float
    description: str
    date: datetime

