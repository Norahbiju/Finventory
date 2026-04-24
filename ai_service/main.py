import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
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
    client = genai.Client(
        api_key=api_key.strip(),
        http_options={'api_version': 'v1'}
    )
else:
    client = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    if not client:
        # Mock response if no key is provided
        return QueryResponse(response=f"[MOCK AI]: I received: '{request.query}'. Please add GEMINI_API_KEY to your .env file to enable the real AI!")
        
    try:
        prompt = f"You are NexaFlow AI Copilot, a helpful financial and inventory assistant. Provide concise, professional answers. User query: {request.query}"
        
        try:
            # First try the absolute latest stable model
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
        except Exception:
            # Fallback to the standard 1.5-flash if 2.0 isn't available for their key
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
        return QueryResponse(response=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"service": "AI Copilot", "status": "running"}
