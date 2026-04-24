from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)       # "income" or "expense"
    category = Column(String, nullable=False)   # "sale", "purchase", "other"
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    product_id = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String(50), nullable=True)
    is_ocr = Column(Boolean, default=False)
