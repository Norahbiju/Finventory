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
    user_id = str(user.get("sub", "1"))
    if user.get("role") == "admin":
        return db.query(models.Transaction).order_by(models.Transaction.created_at.desc()).all()
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).order_by(models.Transaction.created_at.desc()).all()


@router.post("/transactions", response_model=schemas.TransactionOut, status_code=201)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    # Reduce stock automatically on a sale
    user_id = str(user.get("sub", "1"))
    if tx.category == "sale" and tx.product_id and tx.quantity:
        row = db.execute(
            text("SELECT id, stock FROM products WHERE id = :id AND user_id = :uid"),
            {"id": tx.product_id, "uid": user_id}
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found or not owned by user")
        if row.stock < tx.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {row.stock}")
        db.execute(
            text("UPDATE products SET stock = stock - :qty WHERE id = :id AND user_id = :uid"),
            {"qty": tx.quantity, "id": tx.product_id, "uid": user_id}
        )

    new_tx = models.Transaction(
        type=tx.type,
        category=tx.category,
        amount=tx.amount,
        description=tx.description,
        product_id=tx.product_id,
        quantity=tx.quantity,
        user_id=user_id,
        is_ocr=tx.is_ocr or False
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx
