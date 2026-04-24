from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    type: str           # "income" or "expense"
    category: str       # "sale", "purchase", "other"
    amount: float
    description: Optional[str] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    is_ocr: Optional[bool] = False


class TransactionOut(BaseModel):
    id: int
    type: str
    category: str
    amount: float
    description: Optional[str]
    product_id: Optional[int]
    quantity: Optional[int]
    is_ocr: bool
    created_at: datetime

    class Config:
        from_attributes = True
