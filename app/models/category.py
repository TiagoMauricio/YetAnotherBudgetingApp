from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.encryption import encrypt_field, decrypt_field


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name_encrypted = Column(String, nullable=False)
    is_global = Column(Boolean, default=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    transactions = relationship("Transaction", back_populates="category")

    @property
    def name(self):
        return decrypt_field(self.name_encrypted)

    @name.setter
    def name(self, value):
        self.name_encrypted = encrypt_field(value)
