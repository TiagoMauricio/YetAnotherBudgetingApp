from pydantic import BaseModel
from datetime import datetime

class TransactionCreate(BaseModel):
    """Base schema for transactions"""
    account_id: int
    category_id: int
    type: int
    amount: float
    description: str
    date: datetime

class TransactionResponse(BaseModel):
    """Base schema for transaction responses"""
    category: str
    type: str
    amount: float
    description: str
    date: datetime
