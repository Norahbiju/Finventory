# Finventory

A simple full-stack inventory & finance management app built with **FastAPI + PostgreSQL + HTML/CSS/JS**.

---

## Project Structure

```
Finventory/
├── auth_service/        → Port 8001  (Login, Signup, JWT, User list)
├── inventory_service/   → Port 8002  (Product CRUD, stock levels)
├── finance_service/     → Port 8003  (Income & expense transactions)
├── invoice_service/     → Port 8004  (Invoice generation, recommendations)
├── frontend/            → Static HTML pages (open directly in browser)
├── .env                 → Shared environment variables
└── requirements.txt     → Python dependencies
```

---

## Prerequisites

- Python 3.10+
- PostgreSQL running locally
- `pip` package manager

---

## Setup

### 1. Create the database

Open `psql` or pgAdmin and run:

```sql
CREATE DATABASE finventory_db;
```

### 2. Configure environment

Edit `.env` with your PostgreSQL credentials:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finventory_db
SECRET_KEY=finventory_super_secret_key_2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Install dependencies

```bash
cd Finventory
pip install -r requirements.txt
```

### 4. Start all 4 services (open 4 terminal tabs)

```bash
# Terminal 1 — Auth Service
uvicorn auth_service.main:app --port 8001 --reload

# Terminal 2 — Inventory Service
uvicorn inventory_service.main:app --port 8002 --reload

# Terminal 3 — Finance Service
uvicorn finance_service.main:app --port 8003 --reload

# Terminal 4 — Invoice Service
uvicorn invoice_service.main:app --port 8004 --reload
```

> **Note:** Start the Inventory Service first so the `products` table is created before Finance and Invoice services use it.

---

## Using the App

Open `frontend/login.html` directly in your browser.

| Page | File | URL |
|---|---|---|
| Login / Signup | `login.html` | open in browser |
| User Dashboard | `dashboard.html` | auto-redirect after login |
| Admin Dashboard | `admin.html` | auto-redirect if role=admin |
| Inventory | `inventory.html` | nav link |
| Finance | `finance.html` | nav link |

---

## API Reference

| Service | Base URL | Docs |
|---|---|---|
| Auth | `http://localhost:8001` | `/docs` |
| Inventory | `http://localhost:8002` | `/docs` |
| Finance | `http://localhost:8003` | `/docs` |
| Invoice | `http://localhost:8004` | `/docs` |

All services expose Swagger UI at `/docs`.

---

## Database Schema

| Table | Service | Purpose |
|---|---|---|
| `users` | Auth | Login accounts |
| `products` | Inventory | Product catalog + stock |
| `transactions` | Finance | Income & expense records |
| `invoices` | Invoice | Generated invoice records |

---

## Features

- ✅ JWT login & signup (admin / user roles)
- ✅ Admin sees only the user list
- ✅ Add, edit, delete products
- ✅ Stock color badges (red < 10, yellow < 30, green ≥ 30)
- ✅ Record income/expense transactions
- ✅ Auto stock reduction on sale
- ✅ Generate invoices for sale transactions
- ✅ Recommendations: low stock, high expenses, zero-sales products
- ✅ Dashboard summary cards
