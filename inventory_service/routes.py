import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt, JWTError
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


@router.get("/products", response_model=List[schemas.ProductOut])
def get_products(db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    user_id = str(user.get("sub", "1"))
    # Admin sees all? Optional, but keeping strict isolation
    if user.get("role") == "admin":
        return db.query(models.Product).all()
    return db.query(models.Product).filter(models.Product.user_id == user_id).all()


@router.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        user_id=str(user.get("sub", "1"))
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if user.get("role") != "admin" and db_product.user_id != str(user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized to edit this product")
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user: dict = Depends(verify_token)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if user.get("role") != "admin" and db_product.user_id != str(user.get("sub")):
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}
