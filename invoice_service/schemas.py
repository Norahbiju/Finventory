from pydantic import BaseModel
from datetime import datetime


class InvoiceCreate(BaseModel):
    transaction_id: int
    product_name: str
    quantity: int
    unit_price: float


class InvoiceOut(BaseModel):
    id: int
    transaction_id: int
    product_name: str
    quantity: int
    unit_price: float
    total: float
    created_at: datetime

    class Config:
        from_attributes = True
