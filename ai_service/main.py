import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="NexaFlow AI Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not HF_API_KEY or HF_API_KEY == "your_huggingface_key_here":
        return QueryResponse(response=f"[MOCK AI]: I received: '{request.query}'. Please add a valid HF_API_KEY to your .env file to enable the Hugging Face AI!")
        
    headers = {
        "Authorization": f"Bearer {HF_API_KEY.strip()}"
    }

    prompt = f"""You are an AI assistant for a business dashboard.

Inventory Data:
- Shoes: 50 units, ₹500 profit
- Bags: 20 units, ₹200 profit

Finance Data:
- Total revenue: ₹10,000
- Total expenses: ₹7,000

User question:
{request.query}

Answer in simple, clear English."""

    payload = {
        "inputs": prompt,
        "parameters": {
            "return_full_text": False,
            "max_new_tokens": 150
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            answer = result[0]["generated_text"].strip()
            return QueryResponse(response=answer)
        else:
            return QueryResponse(response="I couldn't generate a proper response. Please try again.")

    except requests.exceptions.Timeout:
        return QueryResponse(response="The AI model is currently waking up or took too long to respond. Please try asking again in a few seconds.")
    except Exception as e:
        print(f"Hugging Face API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Hugging Face API. Details: {str(e)}")

@app.get("/")
def root():
    return {"service": "AI Copilot", "status": "running"}
