# NexaFlow — AI-Powered Inventory & Finance Platform

A full-stack SaaS platform built with **FastAPI microservices + PostgreSQL + HTML/CSS/JS + Docker**.

---

## Project Structure

```
Finventory/
├── auth_service/        → Port 8001  (Login, Signup, JWT, User list)
├── inventory_service/   → Port 8002  (Product CRUD, stock levels)
├── finance_service/     → Port 8003  (Income & expense transactions)
├── invoice_service/     → Port 8004  (Invoice PDF + GST + Stock Forecasting)
├── ai_service/          → Port 8005  (AI Financial Copilot via OpenAI)
├── ocr_service/         → Port 8007  (Smart receipt OCR scanning)
├── frontend/            → Nginx-served HTML pages + reverse proxy
├── .env                 → Shared environment variables
└── requirements.txt     → Python dependencies
```

---

## Prerequisites

- Docker & Docker Compose

---

## Setup (Docker — Recommended)

### 1. Configure environment

Edit `.env`:

```
DATABASE_URL=postgresql://postgres:postgres@db:5432/finventory_db
SECRET_KEY=finventory_super_secret_key_2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
OPENAI_API_KEY=sk-your-openai-api-key-here
```

> If `OPENAI_API_KEY` is left blank, the AI Copilot returns a mock response — all other features work normally.

### 2. Start the stack

```bash
docker-compose up -d --build
```

### 3. Open the app

Visit `http://localhost` in your browser.

> **Default login:** username `biju` / password `12345`

---

## API Reference

| Service | Internal Port | Nginx Route |
|---|---|---|
| Auth | 8001 | `/api/auth/` |
| Inventory | 8002 | `/api/inventory/` |
| Finance | 8003 | `/api/finance/` |
| Invoice + Analytics | 8004 | `/api/invoice/` |
| AI Copilot | 8005 | `/api/ai/` |
| OCR | 8007 | `/api/ocr/` |

All services expose Swagger UI at `/docs` on their respective port.

---

## Features

- ✅ JWT login & signup (admin / user roles)
- ✅ Add, edit, delete products with stock tracking
- ✅ Record income/expense transactions
- ✅ Auto stock reduction on sale
- ✅ **Backend PDF Invoice generation** with 18% GST (ReportLab)
- ✅ **AI Financial Copilot** — ask questions in natural language
- ✅ **Predictive Analytics** — per-product stock forecasting dashboard
- ✅ **Smart OCR** — upload receipt photos to auto-fill transactions
- ✅ Recommendations: low stock, high expenses, zero-sales alerts
- ✅ Dashboard summary cards + Cash Flow chart

---

## Deployment (AWS EC2)

```bash
# Pull latest code
git pull

# Rebuild without losing database data
docker-compose down
docker-compose up -d --build
```

> ⚠️ Never run `docker-compose down -v` — this deletes your PostgreSQL data volume.
