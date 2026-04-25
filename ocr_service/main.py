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
    # Accept all file types - let PIL decide if it's a valid image
    try:
        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
        except Exception:
            raise HTTPException(status_code=400, detail="Could not open file as an image. Please upload a PNG, JPG, or JPEG.")

        # Convert to RGB if needed (handles PNG with transparency etc.)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)

        # ── Amount Extraction ────────────────────────────────────────────
        amount = 0.0

        # Strategy: scan line-by-line and take the LAST match for total keywords.
        # Receipts show running subtotals before the final grand total at the bottom.
        TOTAL_KEYWORDS = re.compile(
            r'\b(grand\s+total|total\s+amount|amount\s+payable|net\s+payable|'
            r'net\s+total|balance\s+due|amount\s+due|total)\b',
            re.IGNORECASE
        )
        CURRENCY_PATTERN = re.compile(
            r'(?:rs\.?|inr|₹|\$)?\s*([\d,]+\.?\d{0,2})',
            re.IGNORECASE
        )

        best_amount = 0.0
        for line in text.splitlines():
            if TOTAL_KEYWORDS.search(line):
                # Find all numbers on this line
                nums = CURRENCY_PATTERN.findall(line)
                for n in nums:
                    try:
                        val = float(n.replace(',', ''))
                        if 0 < val < 10_000_000:
                            best_amount = val   # keep the last / largest on a totals line
                    except ValueError:
                        pass

        if best_amount > 0:
            amount = best_amount
        else:
            # Fallback 1: INR symbol anywhere in text
            inr_match = re.search(
                r'(?:INR|Rs\.?|₹)\s*([\d,]+\.?\d{0,2})',
                text, re.IGNORECASE
            )
            if inr_match:
                amount = float(inr_match.group(1).replace(',', ''))
            else:
                # Fallback 2: largest reasonable decimal number
                amounts = re.findall(r'\b(\d{1,6}(?:,\d{3})*(?:\.\d{1,2})?)\b', text)
                parsed = []
                for a in amounts:
                    try:
                        v = float(a.replace(',', ''))
                        if 0 < v < 1_000_000:
                            parsed.append(v)
                    except ValueError:
                        pass
                amount = max(parsed) if parsed else 0.0

        # ── Date Extraction ──────────────────────────────────────────────
        date_match = re.search(
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{2}[/-]\d{2})\b',
            text
        )
        date = date_match.group(1) if date_match else "2026-04-20"

        # ── Vendor Extraction ────────────────────────────────────────────
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]

        # Look for organization name keywords at the bottom (common in Indian receipts)
        vendor = "Unknown Vendor"
        org_keywords = ['university', 'college', 'institute', 'bank', 'store',
                        'pvt', 'ltd', 'llp', 'hospital', 'school', 'traders',
                        'enterprises', 'solutions', 'services']

        # Search from bottom-up for a line with an org keyword
        for line in reversed(lines):
            if any(kw in line.lower() for kw in org_keywords):
                vendor = line
                break
        else:
            # Fallback to first non-generic header line
            skip = ['receipt', 'invoice', 'bill', 'payment']
            for line in lines:
                if not any(s in line.lower() for s in skip) and len(line) > 5:
                    vendor = line
                    break

        return {
            "amount": amount,
            "date": date,
            "vendor": vendor,
            "raw_text": text
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


@app.get("/")
def root():
    return {"service": "OCR Service", "status": "running"}
