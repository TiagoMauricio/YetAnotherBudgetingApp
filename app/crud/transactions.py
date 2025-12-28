from fastapi import HTTPException
from sqlmodel import Session
from app.models import Account, Transaction, User
from app.crud import accounts as acc_crud
from app.schemas.transactions import TransactionResponse


def find_transaction_by_id(transaction_id: int, session: Session) -> Transaction | None:
    return session.get(Transaction, transaction_id)


def create_transaction(
    transaction_data: TransactionResponse, user: User, session: Session
):

    account: Account = acc_crud.get_account_by_id(
        transaction_data.account_id, user, session
    )
    new_transaction: Transaction = Transaction(
        account_id=account.id,
        category_id=transaction_data.category_id,
        user_id=user.id,
        type=transaction_data.type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        date=transaction_data.date,
    )
    session.add(new_transaction)
    session.commit()
    session.refresh(new_transaction)

    return new_transaction
