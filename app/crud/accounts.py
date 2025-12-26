from fastapi import HTTPException
from sqlmodel import Session, select
from collections.abc import Sequence
from sqlmodel.sql.expression import SelectOfScalar
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from app.models import Account, AccountMembership, User
from app.schemas.accounts import AccountBase, AccountUpdate


def get_all_accounts(session: Session) -> Sequence[Account]:
    """Get all accounts"""
    query: SelectOfScalar[Account] = select(Account).order_by(Account.created_at.desc())
    result: Sequence[Account] = session.exec(query).all()
    return result


def create_account(account: AccountBase, user: User, session: Session) -> Account:
    """Create a new account and assign the creator as owner"""

    user_accounts = get_accounts_by_user(user_id=user.id, session=session)

    if account.name in [acc.name for acc in user_accounts]:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"You already have an account named: {account.name}"
        )

    new_account: Account = Account(
        name=account.name,
        currency_code=account.currency_code,
        description=account.description
    )
    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    # Create membership record with owner role
    membership = AccountMembership(
        account_id=new_account.id,
        user_id=user.id,
        role="owner",
        is_owner=True
    )
    session.add(membership)
    session.commit()

    return new_account


def get_account_by_id(account_id: int, user: User, session: Session) -> Account | None:
    """Get account by ID"""
    user_accounts = get_accounts_by_user(user_id=user.id, session=session)
    if account_id not in [acc.id for acc in user_accounts]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN
        )
    return session.get(Account, account_id)


def get_accounts_by_user(user_id: int, session: Session) -> Sequence[Account]:
    """Get all accounts that a user has access to"""
    query = (
        select(Account)
        .join(AccountMembership)
        .where(AccountMembership.user_id == user_id)
        .order_by(Account.created_at.desc())
    )
    return session.exec(query).all()


def get_user_owned_accounts(user_id: int, session: Session) -> Sequence[Account]:
    """Get all accounts owned by a user"""
    query = (
        select(Account)
        .join(AccountMembership)
        .where(
            AccountMembership.user_id == user_id,
            AccountMembership.is_owner == True
        )
        .order_by(Account.created_at.desc())
    )
    return session.exec(query).all()


def update_account(account_id: int, account_data: AccountUpdate, user: User, session: Session) -> Account | None:
    """Update account details"""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Account does not exist."
        )
    elif not user_is_account_owner(user.id, account_id, session):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You do not own this account."
        )

    update_data = account_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(account, field, value)

    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def delete_account(account_id: int, session: Session) -> bool:
    """Delete an account and all its memberships"""
    account = session.get(Account, account_id)
    if not account:
        return False

    # Delete all memberships first
    membership_query = select(AccountMembership).where(AccountMembership.account_id == account_id)
    memberships = session.exec(membership_query).all()
    for membership in memberships:
        session.delete(membership)

    # Delete the account
    session.delete(account)
    session.commit()
    return True


def add_user_to_account(account_id: int, user_id: int, session: Session, role: str = "member") -> AccountMembership | None:
    """Add a user to an account with specified role"""
    # Check if membership already exists
    existing_query = select(AccountMembership).where(
        AccountMembership.account_id == account_id,
        AccountMembership.user_id == user_id
    )
    existing = session.exec(existing_query).first()
    if existing:
        return existing

    # Verify account and user exist
    account = session.get(Account, account_id)
    user = session.get(User, user_id)
    if not account or not user:
        return None

    membership = AccountMembership(
        account_id=account_id,
        user_id=user_id,
        role=role,
        is_owner=False
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def remove_user_from_account(account_id: int, user_id: int, session: Session) -> bool:
    """Remove a user from an account"""
    query = select(AccountMembership).where(
        AccountMembership.account_id == account_id,
        AccountMembership.user_id == user_id,
        AccountMembership.is_owner == False  # Cannot remove owner
    )
    membership = session.exec(query).first()
    if not membership:
        return False

    session.delete(membership)
    session.commit()
    return True


def get_account_members(account_id: int, session: Session) -> Sequence[dict]:
    """Get all members of an account with their details"""
    query = (
        select(User, AccountMembership)
        .join(AccountMembership, User.id == AccountMembership.user_id)
        .where(AccountMembership.account_id == account_id)
        .order_by(AccountMembership.is_owner.desc(), AccountMembership.joined_at)
    )
    results = session.exec(query).all()

    members = []
    for user, membership in results:
        members.append({
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "role": membership.role,
            "is_owner": membership.is_owner,
            "joined_at": membership.joined_at
        })

    return members


def user_has_account_access(user_id: int, account_id: int, session: Session) -> bool:
    """Check if a user has access to an account"""
    query = select(AccountMembership).where(
        AccountMembership.user_id == user_id,
        AccountMembership.account_id == account_id
    )
    return session.exec(query).first() is not None


def user_is_account_owner(user_id: int, account_id: int, session: Session) -> bool:
    """Check if a user is the owner of an account"""
    query = select(AccountMembership).where(
        AccountMembership.user_id == user_id,
        AccountMembership.account_id == account_id,
        AccountMembership.is_owner == True
    )
    account = session.exec(query).first()
    return account is not None
