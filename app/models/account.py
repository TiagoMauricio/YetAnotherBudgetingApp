from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", backref="account")
    entries = relationship("Entry", backref="account")
