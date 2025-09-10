from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.crud.entry import (
    create_entry,
    get_entry,
    get_entries,
    update_entry,
    delete_entry,
    get_entries_by_category,
    get_entries_by_account
)
from app.crud.account import get_account
from app.database import SessionLocal
from app.models.user import User
from app.schemas.entry import EntryCreate, EntryUpdate, EntryOut
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/entries", tags=["entries"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=EntryOut, status_code=status.HTTP_201_CREATED)
async def create_new_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new financial entry (transaction)"""
    # Verify the account exists and user has access to it
    account = get_account(db, account_id=entry.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not any(member.user_id == current_user.id for member in account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to add entries to this account"
        )
    
    return create_entry(db=db, entry=entry, user_id=current_user.id)


@router.get("/", response_model=List[EntryOut])
async def list_entries(
    account_id: Optional[UUID] = Query(None, description="Filter by account ID"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List financial entries with optional filtering"""
    if account_id:
        # Verify user has access to the account
        account = get_account(db, account_id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if not any(member.user_id == current_user.id for member in account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view entries for this account"
            )
        
        if category_id:
            return get_entries_by_category(
                db=db,
                account_id=account_id,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit
            )
        else:
            return get_entries_by_account(
                db=db,
                account_id=account_id,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit
            )
    else:
        # Get all entries across all accounts the user has access to
        return get_entries(
            db=db,
            user_id=current_user.id,
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )


@router.get("/{entry_id}", response_model=EntryOut)
async def get_entry_details(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get details of a specific entry"""
    db_entry = get_entry(db, entry_id=entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Verify user has access to the account this entry belongs to
    account = get_account(db, account_id=db_entry.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not any(member.user_id == current_user.id for member in account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this entry"
        )
    
    return db_entry


@router.put("/{entry_id}", response_model=EntryOut)
async def update_entry_details(
    entry_id: UUID,
    entry_update: EntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing entry"""
    # First get the existing entry
    db_entry = get_entry(db, entry_id=entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Verify user has access to the account this entry belongs to
    account = get_account(db, account_id=db_entry.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not any(member.user_id == current_user.id for member in account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this entry"
        )
    
    # If changing accounts, verify access to the new account
    if entry_update.account_id and entry_update.account_id != db_entry.account_id:
        new_account = get_account(db, account_id=entry_update.account_id)
        if not new_account:
            raise HTTPException(status_code=404, detail="New account not found")
        
        if not any(member.user_id == current_user.id for member in new_account.members):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to move entry to the specified account"
            )
    
    return update_entry(db, entry_id=entry_id, entry=entry_update)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an entry"""
    # First get the existing entry
    db_entry = get_entry(db, entry_id=entry_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Verify user has access to the account this entry belongs to
    account = get_account(db, account_id=db_entry.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not any(member.user_id == current_user.id for member in account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this entry"
        )
    
    delete_entry(db, entry_id=entry_id)
    return {"ok": True}
