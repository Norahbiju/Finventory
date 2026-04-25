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
        lines_list = text.splitlines()

        # MONEY pattern: numbers that MUST have 2 decimal places (e.g. 944.00, 1,200.50)
        # This intentionally excludes integers like 560001, 9608, 4820 (PIN / HSN codes)
        MONEY_RE = re.compile(r'\b(\d{1,7}(?:,\d{3})*\.\d{2})\b')

        # Total keyword priorities (more specific = higher priority)
        HIGH_PRIORITY = re.compile(
            r'\b(grand\s+total|total\s+amount|net\s+payable|amount\s+payable'
            r'|balance\s+due|amount\s+due|net\s+total)\b',
            re.IGNORECASE
        )
        LOW_PRIORITY = re.compile(r'\btotal\b', re.IGNORECASE)

        # ── Strategy 1: High-priority keyword + same line OR next line ──
        for i, line in enumerate(lines_list):
            if HIGH_PRIORITY.search(line):
                # Look at current line AND next line (multi-column OCR splits)
                search_text = line + ' ' + (lines_list[i + 1] if i + 1 < len(lines_list) else '')
                matches = MONEY_RE.findall(search_text)
                for m in matches:
                    val = float(m.replace(',', ''))
                    if val > 0:
                        amount = val  # keep overwriting; last high-priority match wins

        # ── Strategy 2: Low-priority keyword + same/next line ───────────
        if amount == 0:
            for i, line in enumerate(lines_list):
                if LOW_PRIORITY.search(line):
                    search_text = line + ' ' + (lines_list[i + 1] if i + 1 < len(lines_list) else '')
                    matches = MONEY_RE.findall(search_text)
                    for m in matches:
                        val = float(m.replace(',', ''))
                        if val > 0:
                            amount = val

        # ── Strategy 3: Last ₹/Rs/INR amount in the entire text ─────────
        if amount == 0:
            inr_amounts = re.findall(
                r'(?:₹|Rs\.?|INR)\s*(\d{1,7}(?:,\d{3})*\.\d{2})',
                text, re.IGNORECASE
            )
            if inr_amounts:
                # Take the LAST one — bottom of receipt = final total
                amount = float(inr_amounts[-1].replace(',', ''))

        # ── Strategy 4: Fallback — largest decimal (NOT integer) ─────────
        if amount == 0:
            decimal_amounts = MONEY_RE.findall(text)
            parsed = []
            for a in decimal_amounts:
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
