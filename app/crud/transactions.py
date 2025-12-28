from sqlmodel import Session
from app.models import Transaction

def find_transaction_by_id(transaction_id: int, session: Session) -> Transaction | None:
    return session.get(Transaction, transaction_id)
