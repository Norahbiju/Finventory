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

        # Extract text using Tesseract with PSM 4 (Assume a single column of text of variable sizes)
        # This prevents Tesseract from stopping or skipping sections due to dashed lines on receipts
        text = pytesseract.image_to_string(image, config='--psm 4')

        # ── Amount Extraction ────────────────────────────────────────────
        amount = 0.0
        lines_list = text.splitlines()

        # Strict: requires .XX decimals  — used only in fallback to exclude PIN/HSN codes
        MONEY_RE = re.compile(r'(?<!\d)(\d{1,7}(?:,\d{3})*\.\d{1,2})(?!\d)')

        # Flexible: any reasonable number (with or without decimal) — used near keywords
        ANY_NUM  = re.compile(r'(?<!\d)(\d{1,7}(?:[,]\d{3})*(?:[.,]\d{1,2})?)(?!\d)')

        HIGH_PRIORITY = re.compile(
            r'\b(grand\s+total|total\s+amount|net\s+payable|amount\s+payable'
            r'|balance\s+due|amount\s+due|net\s+total)\b',
            re.IGNORECASE
        )
        LOW_PRIORITY = re.compile(r'\btotal\b', re.IGNORECASE)

        def parse_num(s):
            """Normalise comma/dot separators and return float, or None."""
            s = s.strip().replace(',', '')
            try:
                return float(s)
            except ValueError:
                return None

        # ── Strategy 1: High-priority keyword → current + next 3 lines ────
        high_vals = []
        for i, line in enumerate(lines_list):
            if HIGH_PRIORITY.search(line):
                chunk = " ".join(lines_list[i:i+4])
                for m in ANY_NUM.findall(chunk):
                    v = parse_num(m)
                    # Ignore single digits (tax %) and ensure realistic totals
                    if v and v >= 10 and v < 10_000_000:
                        high_vals.append(v)
        if high_vals:
            amount = max(high_vals)

        # ── Strategy 2: Low-priority keyword → current + next 3 lines ─────
        if amount == 0:
            low_vals = []
            for i, line in enumerate(lines_list):
                if LOW_PRIORITY.search(line):
                    chunk = " ".join(lines_list[i:i+4])
                    for m in ANY_NUM.findall(chunk):
                        v = parse_num(m)
                        if v and v >= 10 and v < 10_000_000:
                            low_vals.append(v)
            if low_vals:
                amount = max(low_vals)

        # ── Strategy 3: Last ₹ / Rs / INR amount anywhere in text ────────
        if amount == 0:
            inr_amounts = re.findall(
                r'(?:₹|Rs\.?|INR)\s*(\d{1,7}(?:[,\s]\d{3})*(?:[.,]\d{1,2})?)',
                text, re.IGNORECASE
            )
            for raw in reversed(inr_amounts):
                v = parse_num(raw)
                if v and v > 0:
                    amount = v
                    break

        # ── Strategy 4: Fallback — largest number WITH decimal (not PIN/HSN)
        if amount == 0:
            parsed = []
            for m in MONEY_RE.findall(text):
                v = parse_num(m)
                if v and 0 < v < 1_000_000:
                    parsed.append(v)
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
