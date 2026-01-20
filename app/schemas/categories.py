from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Base schema for category responses"""

    id: int
    account_id: int | None
    name: str
    is_expense: bool
    is_default: bool
