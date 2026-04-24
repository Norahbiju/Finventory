from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database import Base, engine
from .routes import router

# Simple migrations
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS user_id VARCHAR(50) DEFAULT '1'"))
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS is_ocr BOOLEAN DEFAULT FALSE"))
        conn.commit()
except Exception:
    pass

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finventory — Finance Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, tags=["Finance"])


@app.get("/")
def root():
    return {"service": "Finance Service", "status": "running", "port": 8003}
