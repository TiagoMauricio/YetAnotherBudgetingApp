from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.account import Account, AccountMembership, AccountRole
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountMemberUpdate

def get_account(db: Session, account_id: UUID) -> Optional[Account]:
    """Get an account by ID"""
    return db.query(Account).filter(Account.id == account_id).first()

def get_accounts(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Account]:
    """Get all accounts for a specific user"""
    return (
        db.query(Account)
        .join(AccountMembership)
        .filter(AccountMembership.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_account(
    db: Session,
    account: AccountCreate,
    owner_id: UUID
) -> Account:
    """Create a new account"""
    db_account = Account(
        name=account.name,
        description=account.description,
        currency=account.currency,
        balance=account.balance or 0.0,
        owner_id=owner_id
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # Add the owner as an admin member
    add_account_member(
        db=db,
        account_id=db_account.id,
        user_id=owner_id,
        role=AccountRole.ADMIN
    )
    
    return db_account

def update_account(
    db: Session,
    account_id: UUID,
    account: AccountUpdate
) -> Optional[Account]:
    """Update an account"""
    db_account = get_account(db, account_id=account_id)
    if not db_account:
        return None
    
    update_data = account.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_account, field, value)
    
    db_account.updated_at = datetime.utcnow()
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: UUID) -> bool:
    """Delete an account"""
    db_account = get_account(db, account_id=account_id)
    if not db_account:
        return False
    
    db.delete(db_account)
    db.commit()
    return True

def get_account_member(
    db: Session,
    account_id: UUID,
    user_id: UUID
) -> Optional[AccountMembership]:
    """Get a specific account member"""
    return (
        db.query(AccountMembership)
        .filter(
            and_(
                AccountMembership.account_id == account_id,
                AccountMembership.user_id == user_id
            )
        )
        .first()
    )

def get_account_members(db: Session, account_id: UUID) -> List[dict]:
    """Get all members of an account with user details"""
    members = (
        db.query(AccountMembership, User)
        .join(User, AccountMembership.user_id == User.id)
        .filter(AccountMembership.account_id == account_id)
        .all()
    )
    
    return [
        {
            "user_id": member.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "role": member.role,
            "joined_at": member.joined_at,
            "is_owner": member.account.owner_id == member.user_id
        }
        for member, user in members
    ]

def add_account_member(
    db: Session,
    account_id: UUID,
    user_id: UUID,
    role: AccountRole = AccountRole.MEMBER
) -> Optional[AccountMembership]:
    """Add a member to an account"""
    # Check if user is already a member
    existing = get_account_member(db, account_id=account_id, user_id=user_id)
    if existing:
        return existing
    
    db_membership = AccountMembership(
        account_id=account_id,
        user_id=user_id,
        role=role
    )
    
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def update_account_member(
    db: Session,
    account_id: UUID,
    user_id: UUID,
    role: AccountRole
) -> Optional[AccountMembership]:
    """Update a member's role in an account"""
    db_membership = get_account_member(db, account_id=account_id, user_id=user_id)
    if not db_membership:
        return None
    
    db_membership.role = role
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def remove_account_member(
    db: Session,
    account_id: UUID,
    user_id: UUID
) -> bool:
    """Remove a member from an account"""
    db_membership = get_account_member(db, account_id=account_id, user_id=user_id)
    if not db_membership:
        return False
    
    db.delete(db_membership)
    db.commit()
    return True
