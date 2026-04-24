import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from . import models, schemas
from .database import get_db, engine

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


# ── Predictive Analytics (merged from analytics_service) ──────────────
@router.get("/forecast/{product_id}")
def get_forecast(product_id: int, user: dict = Depends(verify_token)):
    try:
        with engine.connect() as conn:
            prod = conn.execute(
                text("SELECT name, stock FROM products WHERE id = :pid"),
                {"pid": product_id}
            ).fetchone()
            if not prod:
                raise HTTPException(status_code=404, detail="Product not found")

            tx_count = conn.execute(
                text("SELECT COALESCE(SUM(quantity), 0) as total FROM transactions WHERE product_id = :pid AND category = 'sale'"),
                {"pid": product_id}
            ).fetchone()[0]

            daily_rate = max(tx_count / 30.0, 0.5)
            days_left = int(prod.stock / daily_rate)

            return {
                "product": prod.name,
                "current_stock": prod.stock,
                "daily_sales_rate": round(daily_rate, 2),
                "days_left": days_left,
                "message": f"Stock will run out in {days_left} days"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/invoices", response_model=List[schemas.InvoiceOut])
def get_invoices(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_id = str(user.get("sub", "1"))
    if user.get("role") == "admin":
        return db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()
    return db.query(models.Invoice).filter(models.Invoice.user_id == user_id).order_by(models.Invoice.created_at.desc()).all()


@router.post("/invoices", response_model=schemas.InvoiceOut, status_code=201)
def generate_invoice(data: schemas.InvoiceCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    invoice = models.Invoice(
        transaction_id=data.transaction_id,
        product_name=data.product_name,
        quantity=data.quantity,
        unit_price=data.unit_price,
        total=round(data.quantity * data.unit_price, 2),
        user_id=str(user.get("sub", "1"))
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}/pdf")
def generate_pdf(invoice_id: int, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_id = str(user.get("sub", "1"))
    
    # Allow admin to view any invoice
    if user.get("role") == "admin":
        invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    else:
        invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id, models.Invoice.user_id == user_id).first()
        
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Calculate GST
    subtotal = invoice.total
    gst = round(subtotal * 0.18, 2)
    grand_total = subtotal + gst

    # Create PDF in memory
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "NexaFlow")
    
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 80, f"Invoice #{invoice.id}")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 200, height - 50, f"Date: {invoice.created_at.strftime('%Y-%m-%d')}")
    c.drawString(width - 200, height - 65, f"Company: {user.get('username', 'Unknown Company')}")
    
    # Table Header
    y = height - 150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product / Service")
    c.drawString(300, y, "Qty")
    c.drawString(400, y, "Unit Price")
    c.drawString(500, y, "Total")
    c.line(50, y - 5, width - 50, y - 5)
    
    # Table Row
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, invoice.product_name)
    c.drawString(300, y, str(invoice.quantity))
    c.drawString(400, y, f"INR {invoice.unit_price:.2f}")
    c.drawString(500, y, f"INR {subtotal:.2f}")
    c.line(50, y - 5, width - 50, y - 5)
    
    # Totals
    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(400, y, "Subtotal:")
    c.drawString(500, y, f"INR {subtotal:.2f}")
    
    y -= 20
    c.drawString(400, y, "GST (18%):")
    c.drawString(500, y, f"INR {gst:.2f}")
    
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y, "Grand Total:")
    c.drawString(500, y, f"INR {grand_total:.2f}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.id}.pdf"}
    )


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


@router.get("/notifications")
def get_notifications(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    notifications = []
    user_id = str(user.get("sub", "1"))
    
    recent_products = db.execute(
        text("SELECT id, name, created_at FROM products WHERE user_id = :uid ORDER BY created_at DESC LIMIT 3"),
        {"uid": user_id}
    ).fetchall()
    for p in recent_products:
        notifications.append({"id": f"p_{p.id}", "type": "info", "message": f"New product added: {p.name}", "time": p.created_at})
        
    low_stock = db.execute(
        text("SELECT id, name, stock FROM products WHERE stock < :threshold AND user_id = :uid"), 
        {"threshold": LOW_STOCK_THRESHOLD, "uid": user_id}
    ).fetchall()
    for p in low_stock:
        notifications.append({"id": f"s_{p.id}", "type": "warning", "message": f"Low stock alert: {p.name} ({p.stock} left)", "time": None})
        
    recent_tx = db.execute(
        text("SELECT id, type, amount, created_at FROM transactions WHERE user_id = :uid ORDER BY created_at DESC LIMIT 3"),
        {"uid": user_id}
    ).fetchall()
    for t in recent_tx:
        notifications.append({"id": f"t_{t.id}", "type": "success" if t.type == "income" else "info", "message": f"New {t.type} transaction: ₹{t.amount:.2f}", "time": t.created_at})
        
    recent_inv = db.execute(
        text("SELECT id, product_name, total, created_at FROM invoices WHERE user_id = :uid ORDER BY created_at DESC LIMIT 3"),
        {"uid": user_id}
    ).fetchall()
    for i in recent_inv:
        notifications.append({"id": f"i_{i.id}", "type": "success", "message": f"Invoice #{i.id} generated for {i.product_name} (₹{i.total:.2f})", "time": i.created_at})
        
    notifications.sort(key=lambda x: str(x['time']) if x['time'] else "9999", reverse=True)
    return notifications[:10]
