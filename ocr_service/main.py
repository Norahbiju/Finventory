from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import re
import io

app = FastAPI(title="NexaFlow OCR Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr/upload")
async def process_receipt(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only images are supported for now")
        
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)
        
        # Simple Regex extraction (Very basic approximations)
        # 1. Amount: Look for $ or decimals
        amounts = re.findall(r'\b\d+\.\d{2}\b', text)
        amount = 0.0
        if amounts:
            # Assume the largest number is the total
            amount = max([float(a) for a in amounts])
            
        # 2. Date: Look for YYYY-MM-DD or MM/DD/YYYY
        date_match = re.search(r'(\d{2,4}[-/]\d{2}[-/]\d{2,4})', text)
        date = date_match.group(1) if date_match else "2026-04-20"
        
        # 3. Vendor: Usually the first line of the receipt
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]
        vendor = lines[0] if lines else "Unknown Vendor"
        
        return {
            "amount": amount,
            "date": date,
            "vendor": vendor,
            "raw_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

@app.get("/")
def root():
    return {"service": "OCR Service", "status": "running"}
