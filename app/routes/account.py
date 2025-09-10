from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.account import (
    create_account,
    get_account,
    get_accounts,
    update_account,
    delete_account,
    add_account_member,
    update_account_member,
    remove_account_member,
    get_account_members
)
from app.database import SessionLocal
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut, AccountMemberUpdate
from app.utils.security import get_current_active_user

router = APIRouter(prefix="/accounts", tags=["accounts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_new_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new account"""
    return create_account(db=db, account=account, owner_id=current_user.id)


@router.get("/", response_model=List[AccountOut])
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all accounts for the current user"""
    return get_accounts(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account_details(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get account details by ID"""
    db_account = get_account(db, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check if user has access to this account
    if not any(member.user_id == current_user.id for member in db_account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this account"
        )
    
    return db_account


@router.put("/{account_id}", response_model=AccountOut)
async def update_account_details(
    account_id: UUID,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update account details (account owner only)"""
    db_account = get_account(db, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check if user is the owner
    if db_account.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the account owner can update account details"
        )
    
    return update_account(db, account_id=account_id, account=account_update)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an account (account owner only)"""
    db_account = get_account(db, account_id=account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if db_account.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the account owner can delete the account"
        )
    
    delete_account(db, account_id=account_id)
    return {"ok": True}


@router.get("/{account_id}/members", response_model=List[dict])
async def list_account_members(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all members of an account"""
    # Verify user has access to this account
    account = get_account(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not any(member.user_id == current_user.id for member in account.members):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this account"
        )
    
    return get_account_members(db, account_id=account_id)


@router.post("/{account_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_member_to_account(
    account_id: UUID,
    user_id: UUID,
    member_data: AccountMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a member to an account (account owner only)"""
    account = get_account(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the account owner can add members"
        )
    
    return add_account_member(
        db=db,
        account_id=account_id,
        user_id=user_id,
        role=member_data.role
    )


@router.put("/{account_id}/members/{user_id}")
async def update_account_member(
    account_id: UUID,
    user_id: UUID,
    member_data: AccountMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a member's role in an account (account owner only)"""
    account = get_account(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the account owner can update member roles"
        )
    
    return update_account_member(
        db=db,
        account_id=account_id,
        user_id=user_id,
        role=member_data.role
    )


@router.delete("/{account_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_account(
    account_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a member from an account (account owner only)"""
    account = get_account(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the account owner can remove members"
        )
    
    # Prevent removing the account owner
    if account.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the account owner"
        )
    
    remove_account_member(db, account_id=account_id, user_id=user_id)
    return {"ok": True}
