from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.crud.category import (
    create_category,
    get_category,
    get_categories,
    update_category,
    delete_category,
    get_default_categories
)
from app.crud.account import get_account
from app.database import SessionLocal
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/categories", tags=["categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new category"""
    # Verify the account exists and user has access to it
    if category.account_id:
        account = get_account(db, account_id=category.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to add categories to this account"
            )
    
    return create_category(db=db, category=category)


@router.get("/default", response_model=List[CategoryOut])
async def list_default_categories():
    """List all default categories (no authentication required)"""
    return get_default_categories()


@router.get("/", response_model=List[CategoryOut])
async def list_categories(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    category_type: Optional[str] = Query(
        None, 
        description="Filter by category type",
        regex="^(income|expense)$"
    ),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List categories with optional filtering"""
    if account_id:
        # Verify user has access to the account
        account = get_account(db, account_id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view categories for this account"
            )
    
    return get_categories(
        db=db,
        account_id=account_id,
        category_type=category_type,
        skip=skip,
        limit=limit
    )


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category_details(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get details of a specific category"""
    db_category = get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # For account-specific categories, verify access
    if db_category.account_id:
        account = get_account(db, account_id=db_category.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this category"
            )
    
    return db_category


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category_details(
    category_id: UUID,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing category"""
    db_category = get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # For account-specific categories, verify access
    if db_category.account_id:
        account = get_account(db, account_id=db_category.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to update this category"
            )
    
    return update_category(db, category_id=category_id, category=category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a category"""
    db_category = get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # For account-specific categories, verify access
    if db_category.account_id:
        account = get_account(db, account_id=db_category.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete this category"
            )
    
    delete_category(db, category_id=category_id)
    return {"ok": True}
