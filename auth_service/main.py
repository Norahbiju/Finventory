from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import router

from sqlalchemy import text

# Simple migration for is_blocked
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE"))
        conn.commit()
except Exception:
    pass

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finventory — Auth Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/auth", tags=["Auth"])


@app.get("/")
def root():
    return {"service": "Auth Service", "status": "running", "port": 8001}
