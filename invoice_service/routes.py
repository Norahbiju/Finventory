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
LOW_STOCK_THRESHOLD = 10

router = APIRouter()


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/invoices", response_model=List[schemas.InvoiceOut])
def get_invoices(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    return db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()


@router.post("/invoices/generate", response_model=schemas.InvoiceOut, status_code=201)
def generate_invoice(data: schemas.InvoiceCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    invoice = models.Invoice(
        transaction_id=data.transaction_id,
        product_name=data.product_name,
        quantity=data.quantity,
        unit_price=data.unit_price,
        total=round(data.quantity * data.unit_price, 2),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    recommendations = []

    # 1. Low stock alert
    low_stock = db.execute(
        text("SELECT id, name, stock FROM products WHERE stock < :threshold ORDER BY stock ASC"),
        {"threshold": LOW_STOCK_THRESHOLD},
    ).fetchall()
    for p in low_stock:
        recommendations.append({
            "type": "low_stock",
            "message": f"⚠️ '{p.name}' is running low ({p.stock} units left). Consider restocking soon.",
            "product_id": p.id,
        })

    # 2. High expense warning (expenses > 80% of income)
    expenses_row = db.execute(
        text("SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE type = 'expense'")
    ).fetchone()
    income_row = db.execute(
        text("SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE type = 'income'")
    ).fetchone()
    total_expenses = expenses_row.total
    total_income = income_row.total
    if total_income > 0 and total_expenses >= total_income * 0.8:
        recommendations.append({
            "type": "high_expense",
            "message": f"🔴 Expenses (${total_expenses:,.2f}) are {int(total_expenses/total_income*100)}% of income (${total_income:,.2f}). Review your spending.",
        })

    # 3. Low-selling products (products with zero sales)
    low_selling = db.execute(
        text("""
            SELECT p.id, p.name
            FROM products p
            LEFT JOIN transactions t ON t.product_id = p.id AND t.category = 'sale'
            GROUP BY p.id, p.name
            HAVING COUNT(t.id) = 0
        """)
    ).fetchall()
    for p in low_selling:
        recommendations.append({
            "type": "low_selling",
            "message": f"📉 '{p.name}' has had zero sales. Consider a promotion or price adjustment.",
            "product_id": p.id,
        })

    if not recommendations:
        recommendations.append({
            "type": "ok",
            "message": "✅ Everything looks great! No critical issues detected.",
        })

    return recommendations
