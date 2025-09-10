from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.category import Category, CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: UUID) -> Optional[Category]:
    """Get a category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(
    db: Session,
    account_id: Optional[UUID] = None,
    category_type: Optional[CategoryType] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Category]:
    """Get all categories with optional filtering"""
    query = db.query(Category)

    if account_id is not None:
        query = query.filter(
            or_(
                Category.account_id == account_id,
                Category.is_default.is_(True)  # Include default categories
            )
        )

    if category_type is not None:
        query = query.filter(Category.type == category_type)

    return query.offset(skip).limit(limit).all()


def get_default_categories() -> List[dict]:
    """Get the list of default categories"""
    return [
        {
            "id": str(cat["id"]),
            "name": cat["name"],
            "type": cat["type"],
            "is_default": True,
            "icon": cat.get("icon", ""),
            "color": cat.get("color", "#666666")
        }
        for cat in DEFAULT_CATEGORIES
    ]


def create_category(
    db: Session,
    category: CategoryCreate
) -> Category:
    """Create a new category"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session,
    category_id: UUID,
    category: CategoryUpdate,
) -> Optional[Category]:
    """Update a category.

    Args:
        db: Database session
        category_id: ID of the category to update
        category: Category data to update

    Returns:
        Updated category if successful, None otherwise
    """
    db_category = get_category(db, category_id=category_id)
    if not db_category:
        return None

    # Prevent modifying default categories
    if db_category.is_default:
        return None

    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db_category.updated_at = datetime.utcnow()
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: UUID) -> bool:
    """Delete a category.

    Args:
        db: Database session
        category_id: ID of the category to delete

    Returns:
        bool: True if deleted, False otherwise
    """
    db_category = get_category(db, category_id=category_id)
    if not db_category:
        return False

    # Prevent deleting default categories
    if db_category.is_default:
        return False

    db.delete(db_category)
    db.commit()
    return True


# Default categories that will be available to all users
DEFAULT_CATEGORIES = [
    {
        "id": "1",
        "name": "Salary",
        "type": CategoryType.INCOME,
        "icon": "cash",
        "color": "#4CAF50"
    },
    {
        "id": "2",
        "name": "Freelance",
        "type": CategoryType.INCOME,
        "icon": "laptop",
        "color": "#4CAF50"
    },
    {
        "id": "3",
        "name": "Investments",
        "type": CategoryType.INCOME,
        "icon": "trending-up",
        "color": "#4CAF50"
    },
    {
        "id": "4",
        "name": "Gifts",
        "type": CategoryType.INCOME,
        "icon": "gift",
        "color": "#4CAF50"
    },
    {
        "id": "5",
        "name": "Other Income",
        "type": CategoryType.INCOME,
        "icon": "plus-circle",
        "color": "#4CAF50"
    },
    {
        "id": "6",
        "name": "Housing",
        "type": CategoryType.EXPENSE,
        "icon": "home",
        "color": "#F44336"
    },
    {
        "id": "7",
        "name": "Utilities",
        "type": CategoryType.EXPENSE,
        "icon": "zap",
        "color": "#F44336"
    },
    {
        "id": "8",
        "name": "Groceries",
        "type": CategoryType.EXPENSE,
        "icon": "shopping-cart",
        "color": "#F44336"
    },
    {
        "id": "9",
        "name": "Transportation",
        "type": CategoryType.EXPENSE,
        "icon": "truck",
        "color": "#F44336"
    },
    {
        "id": "10",
        "name": "Entertainment",
        "type": CategoryType.EXPENSE,
        "icon": "film",
        "color": "#F44336"
    },
    {
        "id": "11",
        "name": "Health",
        "type": CategoryType.EXPENSE,
        "icon": "heart",
        "color": "#F44336"
    },
    {
        "id": "12",
        "name": "Shopping",
        "type": CategoryType.EXPENSE,
        "icon": "shopping-bag",
        "color": "#F44336"
    },
    {
        "id": "13",
        "name": "Education",
        "type": CategoryType.EXPENSE,
        "icon": "book",
        "color": "#F44336"
    },
    {
        "id": "14",
        "name": "Travel",
        "type": CategoryType.EXPENSE,
        "icon": "globe",
        "color": "#F44336"
    },
    {
        "id": "15",
        "name": "Other Expense",
        "type": CategoryType.EXPENSE,
        "icon": "minus-circle",
        "color": "#F44336"
    },
    {
        "id": "16",
        "name": "Transfer",
        "type": CategoryType.TRANSFER,
        "icon": "repeat",
        "color": "#2196F3"
    }
]
