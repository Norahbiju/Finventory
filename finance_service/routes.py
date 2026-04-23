import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/transactions", response_model=List[schemas.TransactionOut])
def get_transactions(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return db.query(models.Transaction).order_by(models.Transaction.created_at.desc()).all()


@router.post("/transactions", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    # Reduce stock automatically on a sale
    if tx.category == "sale" and tx.product_id and tx.quantity:
        row = db.execute(
            text("SELECT id, stock FROM products WHERE id = :id"),
            {"id": tx.product_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        if row.stock < tx.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {row.stock}")
        db.execute(
            text("UPDATE products SET stock = stock - :qty WHERE id = :id"),
            {"qty": tx.quantity, "id": tx.product_id}
        )

    new_tx = models.Transaction(**tx.model_dump())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx
