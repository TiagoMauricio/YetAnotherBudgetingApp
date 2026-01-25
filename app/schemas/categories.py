from pydantic import BaseModel


class CategoryCreate(BaseModel):
    """Schema for creating a new category"""

    name: str
    is_expense: bool
    description: str | None = None


class CategoryResponse(CategoryCreate):
    """Base schema for category responses"""

    id: int
    user_id: int | None
