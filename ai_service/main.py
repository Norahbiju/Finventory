import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI(title="NexaFlow AI Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_key_here":
    genai.configure(api_key=GEMINI_API_KEY)
    # Using the standard gemini-pro model for text instructions
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not model:
        return QueryResponse(response=f"[MOCK AI]: I received: '{request.query}'. Please add a valid GEMINI_API_KEY to your .env file to enable the Google Gemini AI!")
        
    prompt = f"""You are an AI assistant for a business dashboard.

Inventory Data:
- Shoes: 50 units, ₹500 profit
- Bags: 20 units, ₹200 profit

Finance Data:
- Total revenue: ₹10,000
- Total expenses: ₹7,000

User question:
{request.query}

Answer in simple, clear English and be extremely concise."""

    try:
        response = model.generate_content(prompt)
        return QueryResponse(response=response.text.strip())
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Gemini API. Details: {str(e)}")

@app.get("/")
def root():
    return {"service": "AI Copilot", "status": "running"}
