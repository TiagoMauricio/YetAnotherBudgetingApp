from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.models.entry import Entry, EntryType
from app.models.account import Account
from app.models.category import Category
from app.schemas.entry import EntryCreate, EntryUpdate

def get_entry(db: Session, entry_id: UUID) -> Optional[Entry]:
    """Get an entry by ID"""
    return db.query(Entry).filter(Entry.id == entry_id).first()

def get_entries(
    db: Session,
    user_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Entry]:
    """Get all entries for a user with optional filtering"""
    query = (
        db.query(Entry)
        .join(Account, Entry.account_id == Account.id)
        .join(Account.members)
        .filter(AccountMembership.user_id == user_id)
    )
    
    if start_date:
        query = query.filter(Entry.date >= start_date)
    if end_date:
        query = query.filter(Entry.date <= end_date)
    if category_id:
        query = query.filter(Entry.category_id == category_id)
    
    return query.offset(skip).limit(limit).all()

def get_entries_by_account(
    db: Session,
    account_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Entry]:
    """Get all entries for a specific account with optional date filtering"""
    query = db.query(Entry).filter(Entry.account_id == account_id)
    
    if start_date:
        query = query.filter(Entry.date >= start_date)
    if end_date:
        query = query.filter(Entry.date <= end_date)
    
    return query.order_by(desc(Entry.date)).offset(skip).limit(limit).all()

def get_entries_by_category(
    db: Session,
    account_id: UUID,
    category_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Entry]:
    """Get all entries for a specific category with optional date filtering"""
    query = (
        db.query(Entry)
        .filter(
            and_(
                Entry.account_id == account_id,
                Entry.category_id == category_id
            )
        )
    )
    
    if start_date:
        query = query.filter(Entry.date >= start_date)
    if end_date:
        query = query.filter(Entry.date <= end_date)
    
    return query.order_by(desc(Entry.date)).offset(skip).limit(limit).all()

def create_entry(
    db: Session,
    entry: EntryCreate,
    user_id: UUID
) -> Entry:
    """Create a new entry"""
    db_entry = Entry(
        **entry.dict(),
        user_id=user_id
    )
    
    db.add(db_entry)
    
    # Update account balance
    account = db.query(Account).filter(Account.id == entry.account_id).first()
    if account:
        if entry.type == EntryType.INCOME:
            account.balance += entry.amount
        else:  # EXPENSE or TRANSFER
            account.balance -= entry.amount
        
        # If this is a transfer, update the target account
        if entry.type == EntryType.TRANSFER and entry.transfer_to_account_id:
            target_account = db.query(Account).filter(Account.id == entry.transfer_to_account_id).first()
            if target_account:
                target_account.balance += entry.amount
                db.add(target_account)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry

def update_entry(
    db: Session,
    db_entry: Entry,
    entry: EntryUpdate
) -> Optional[Entry]:
    """Update an entry"""
    # First, revert the old entry's effect on the account balance
    account = db.query(Account).filter(Account.id == db_entry.account_id).first()
    if account:
        if db_entry.type == EntryType.INCOME:
            account.balance -= db_entry.amount
        else:  # EXPENSE or TRANSFER
            account.balance += db_entry.amount
        
        # If this was a transfer, revert the target account
        if db_entry.type == EntryType.TRANSFER and db_entry.transfer_to_account_id:
            target_account = db.query(Account).filter(Account.id == db_entry.transfer_to_account_id).first()
            if target_account:
                target_account.balance -= db_entry.amount
                db.add(target_account)
    
    # Update entry fields
    update_data = entry.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entry, field, value)
    
    # Apply the new entry's effect on the account balance
    if account:
        if db_entry.type == EntryType.INCOME:
            account.balance += db_entry.amount
        else:  # EXPENSE or TRANSFER
            account.balance -= db_entry.amount
        
        # If this is a transfer, update the target account
        if db_entry.type == EntryType.TRANSFER and db_entry.transfer_to_account_id:
            target_account = db.query(Account).filter(Account.id == db_entry.transfer_to_account_id).first()
            if target_account:
                target_account.balance += db_entry.amount
                db.add(target_account)
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def delete_entry(db: Session, entry_id: UUID) -> bool:
    """Delete an entry"""
    db_entry = get_entry(db, entry_id=entry_id)
    if not db_entry:
        return False
    
    # Revert the entry's effect on the account balance
    account = db.query(Account).filter(Account.id == db_entry.account_id).first()
    if account:
        if db_entry.type == EntryType.INCOME:
            account.balance -= db_entry.amount
        else:  # EXPENSE or TRANSFER
            account.balance += db_entry.amount
        
        # If this was a transfer, revert the target account
        if db_entry.type == EntryType.TRANSFER and db_entry.transfer_to_account_id:
            target_account = db.query(Account).filter(Account.id == db_entry.transfer_to_account_id).first()
            if target_account:
                target_account.balance -= db_entry.amount
                db.add(target_account)
    
    db.delete(db_entry)
    db.commit()
    return True

def get_account_balance(
    db: Session,
    account_id: UUID,
    as_of_date: Optional[date] = None
) -> float:
    """Get the balance of an account as of a specific date"""
    query = db.query(
        func.coalesce(func.sum(
            func.case(
                [
                    (Entry.type == EntryType.INCOME, Entry.amount),
                    (Entry.type.in_([EntryType.EXPENSE, EntryType.TRANSFER]), -Entry.amount)
                ],
                else_=0
            )
        ), 0)
    ).filter(Entry.account_id == account_id)
    
    if as_of_date:
        query = query.filter(Entry.date <= as_of_date)
    
    return query.scalar() or 0.0

def get_category_totals(
    db: Session,
    account_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    entry_type: Optional[EntryType] = None
) -> List[Tuple[Category, float]]:
    """Get totals by category with optional filtering"""
    query = (
        db.query(
            Category,
            func.sum(Entry.amount).label('total')
        )
        .join(Entry, Entry.category_id == Category.id)
        .filter(Entry.account_id == account_id)
        .group_by(Category.id)
    )
    
    if start_date:
        query = query.filter(Entry.date >= start_date)
    if end_date:
        query = query.filter(Entry.date <= end_date)
    if entry_type:
        query = query.filter(Entry.type == entry_type)
    
    return query.all()
