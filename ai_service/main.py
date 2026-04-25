import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from sqlalchemy import create_engine, text

load_dotenv()

app = FastAPI(title="NexaFlow AI Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Gemini Setup ──────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key_here":
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        _models = list(client.models.list())
        # Prefer flash models — much higher free tier rate limit (15 RPM vs 2 RPM for pro)
        SELECTED_MODEL = None
        for m in _models:
            if "flash" in m.name.lower():
                SELECTED_MODEL = m.name
                break
        if not SELECTED_MODEL and _models:
            SELECTED_MODEL = _models[0].name
        print(f"AI Service initialized. Using model: {SELECTED_MODEL}")
    except Exception as e:
        print(f"Warning: Could not list models. Defaulting. Error: {e}")
        SELECTED_MODEL = "gemini-2.0-flash"
else:
    client = None
    SELECTED_MODEL = None

# ── Database Setup ────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")
db_engine = None
if DATABASE_URL:
    try:
        db_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        print("AI Service DB connection established.")
    except Exception as e:
        print(f"AI Service DB connection failed: {e}")


def get_live_business_data() -> str:
    """Query the database for real financial and inventory data."""
    if not db_engine:
        return "Database not available. Using estimated data only."

    try:
        with db_engine.connect() as conn:
            # Finance summary
            finance = conn.execute(text("""
                SELECT
                    COALESCE(SUM(CASE WHEN type='income'  THEN amount ELSE 0 END), 0) AS total_income,
                    COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS total_expenses,
                    COUNT(*) AS total_transactions
                FROM transactions
            """)).fetchone()

            total_income    = float(finance[0])
            total_expenses  = float(finance[1])
            total_txns      = int(finance[2])
            profit          = total_income - total_expenses

            # Recent transactions (last 5)
            recent = conn.execute(text("""
                SELECT type, category, amount, description, created_at
                FROM transactions
                ORDER BY created_at DESC
                LIMIT 5
            """)).fetchall()

            recent_lines = []
            for r in recent:
                recent_lines.append(
                    f"  - [{r[0].upper()}] {r[2]:.2f} | {r[1]} | {r[3] or 'No description'} | {str(r[4])[:10]}"
                )

            # Inventory summary
            inventory = conn.execute(text("""
                SELECT name, price, stock
                FROM products
                ORDER BY stock ASC
            """)).fetchall()

            inv_lines = []
            for item in inventory:
                inv_lines.append(f"  - {item[0]}: {item[2]} units @ ₹{item[1]:.2f} each")

            profit_label = "PROFIT" if profit >= 0 else "LOSS"

            summary = f"""
=== LIVE BUSINESS DATA (from real database) ===

FINANCIAL SUMMARY:
  Total Income:    ₹{total_income:,.2f}
  Total Expenses:  ₹{total_expenses:,.2f}
  Net {profit_label}:    ₹{abs(profit):,.2f}  {"(positive)" if profit >= 0 else "(NEGATIVE — spending more than earning)"}
  Total Transactions: {total_txns}

RECENT TRANSACTIONS (latest 5):
{chr(10).join(recent_lines) if recent_lines else "  No transactions found."}

INVENTORY:
{chr(10).join(inv_lines) if inv_lines else "  No products found."}
"""
            return summary

    except Exception as e:
        print(f"DB query error in AI service: {e}")
        return f"Could not fetch live data: {str(e)}"


# ── API ───────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not client or not SELECTED_MODEL:
        return QueryResponse(
            response="[MOCK AI]: Please add a valid GEMINI_API_KEY to enable the AI Copilot."
        )

    # Fetch real live data from DB
    live_data = get_live_business_data()

    prompt = f"""You are NexaFlow AI Copilot, a smart financial assistant for a small business dashboard.
You have access to the live, real-time data from the business database shown below.
Always base your answers ONLY on this data — never make up or assume numbers.

{live_data}

User question: {request.query}

Rules:
- Be concise and direct (2-3 sentences max).
- Use the exact numbers from the data above.
- If the business is at a loss, clearly say so. Never say "profit" if the net is negative.
- Use ₹ for currency.
- If data is missing or empty, say so honestly.
"""

    try:
        response = client.models.generate_content(
            model=SELECTED_MODEL,
            contents=prompt,
        )
        return QueryResponse(response=response.text.strip())
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
            return QueryResponse(
                response="I'm handling too many requests right now. Please wait 30 seconds and try again."
            )
        raise HTTPException(status_code=500, detail=f"AI error: {error_msg[:120]}")


@app.get("/")
def root():
    return {"service": "AI Copilot", "status": "running", "model": SELECTED_MODEL}
