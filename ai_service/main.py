import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
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

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
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
        # Mock response if no key is provided
        return QueryResponse(response=f"[MOCK AI]: I received: '{request.query}'. Please add GEMINI_API_KEY to your .env file to enable the real AI!")
        
    try:
        prompt = f"You are NexaFlow AI Copilot, a helpful financial and inventory assistant. Provide concise, professional answers. User query: {request.query}"
        response = model.generate_content(prompt)
        return QueryResponse(response=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"service": "AI Copilot", "status": "running"}
