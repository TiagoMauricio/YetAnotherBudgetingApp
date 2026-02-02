from sqlmodel import Session

from app.crud import accounts as acc_crud
from app.crud import categories as cat_crud
from app.models import Account, Transaction, User, Category
from app.schemas.transactions import BaseTransaction, TransactionUpdate
from app.utils.exceptions import exceptions as err
from app.utils.messages import (
    ACCOUNT_NOT_FOUND,
    CATEGORY_NOT_FOUND,
    TRANSACTION_NOT_FOUND,
    TRANSACTION_INVALID_CATEGORY,
)


def find_transaction_by_id(transaction_id: int, session: Session) -> Transaction | None:
    t = session.get(Transaction, transaction_id)
    return t


def create_transaction(transaction_data: BaseTransaction, user: User, session: Session):
    account: Account | None = acc_crud.get_account_by_id(
        transaction_data.account_id, user, session
    )
    if not account:
        raise err.EntityNotFoundException(ACCOUNT_NOT_FOUND)

    category: Category | None = cat_crud.get_category_by_id(
        user, session, transaction_data.category_id
    )
    if not category:
        raise err.EntityNotFoundException(CATEGORY_NOT_FOUND)

    new_transaction: Transaction = Transaction(
        account_id=account.id,
        category_id=transaction_data.category_id,
        user_id=user.id,
        amount=transaction_data.amount,
        description=transaction_data.description,
        date=transaction_data.date,
    )
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    return new_transaction


def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    user: User,
    session: Session,
) -> Transaction | None:
    transaction: Transaction | None = find_transaction_by_id(transaction_id, session)
    if not transaction:
        raise err.EntityNotFoundException(TRANSACTION_NOT_FOUND)

    update_data = transaction_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category: Category | None = cat_crud.get_category_by_id(
            user, session, update_data["category_id"]
        )
        if not category:
            raise err.BadRequestException(TRANSACTION_INVALID_CATEGORY)

    for field, value in update_data.items():
        setattr(transaction, field, value)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def delete_transaction(transaction_id: int, session: Session) -> bool:
    transaction: Transaction | None = find_transaction_by_id(transaction_id, session)
    session.delete(transaction)
    session.commit()
    return True
