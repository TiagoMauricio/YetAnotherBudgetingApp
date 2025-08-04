from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    role = Column(String, nullable=False)
