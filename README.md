# Ethara API

A FastAPI backend for managing products, customers, orders, and a dashboard summary. Uses PostgreSQL for storage and Alembic for database migrations.

## Tech Stack

- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **PostgreSQL** — database
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server

## Prerequisites

- Python 3.9+
- Docker & Docker Compose (for PostgreSQL)
- `pip` and `venv`

## Docker

Run the full stack (PostgreSQL + API) with Docker Compose:

```bash
docker compose up --build
```

The API will be available at **http://127.0.0.1:8000**

Useful commands:

| Command | Description |
|---------|-------------|
| `docker compose up --build -d` | Start in background |
| `docker compose down` | Stop containers (data persists) |
| `docker compose down -v` | Stop and remove database volume |
| `docker compose logs -f api` | Follow API logs |

Migrations run automatically when the API container starts.

For local development without Docker, follow the steps below.

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd ethara-be
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL

```bash
docker compose up -d
```

This starts PostgreSQL on port `5432` with:

| Setting  | Value     |
|----------|-----------|
| User     | `postgres` |
| Password | `postgres` |
| Database | `ethara`   |

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ethara
LOW_STOCK_THRESHOLD=10
```

`DATABASE_URL` and `LOW_STOCK_THRESHOLD` are optional — defaults are defined in `app/core/config.py`.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the API server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**

Interactive API docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Project Structure

```
ethara-be/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic environment config
├── app/
│   ├── api/
│   │   └── routes/             # API route handlers
│   │       ├── customers.py
│   │       ├── dashboard.py
│   │       ├── health.py
│   │       ├── orders.py
│   │       └── products.py
│   ├── core/
│   │   └── config.py           # App settings (env vars)
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # DB engine, session, get_db dependency
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── product.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── customer.py
│   │   ├── dashboard.py
│   │   ├── order.py
│   │   └── product.py
│   └── main.py                 # FastAPI app entry point
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # PostgreSQL service
├── requirements.txt
└── .env                        # Local environment variables (not committed)
```

---

## Database Migrations

All migration commands should be run from the project root with the virtual environment activated.

| Command | Description |
|---------|-------------|
| `alembic upgrade head` | Apply all pending migrations |
| `alembic current` | Show the current migration version |
| `alembic history` | List all migrations |
| `alembic downgrade -1` | Roll back the last migration |
| `alembic revision --autogenerate -m "message"` | Generate a new migration from model changes |

### Typical workflow after changing a model

1. Update the SQLAlchemy model in `app/models/`
2. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "describe your change"
   ```
3. Review the generated file in `alembic/versions/`
4. Apply it:
   ```bash
   alembic upgrade head
   ```

---

## API Endpoints

### Health

| Method | Endpoint   | Description        |
|--------|------------|--------------------|
| GET    | `/health`  | Health check       |

### Products

| Method | Endpoint          | Description          |
|--------|-------------------|----------------------|
| POST   | `/products`       | Create a product     |
| GET    | `/products`       | List all products    |
| GET    | `/products/{id}`  | Get product by ID    |
| PUT    | `/products/{id}`  | Update a product     |
| DELETE | `/products/{id}`  | Delete a product     |

### Customers

| Method | Endpoint            | Description            |
|--------|---------------------|------------------------|
| POST   | `/customers`        | Create a customer      |
| GET    | `/customers`        | List all customers     |
| GET    | `/customers/{id}`   | Get customer by ID     |
| DELETE | `/customers/{id}`   | Delete a customer      |

### Orders

| Method | Endpoint         | Description                          |
|--------|------------------|--------------------------------------|
| POST   | `/orders`        | Create an order (reduces stock)      |
| GET    | `/orders`        | List all orders                      |
| GET    | `/orders/{id}`   | Get order by ID                      |
| DELETE | `/orders/{id}`   | Cancel/delete order (restores stock) |

### Dashboard

| Method | Endpoint      | Description                                      |
|--------|---------------|--------------------------------------------------|
| GET    | `/dashboard`  | Summary: totals + low-stock products             |

---

## Business Rules

- **Product `sku_code`** must be unique
- **Customer `email`** must be unique
- **Product `available_qty`** cannot be negative
- **Orders** are rejected if inventory is insufficient
- **Creating an order** automatically reduces product stock
- **Deleting an order** restores product stock
- **Order total** is calculated automatically by the backend
- **Low stock products** are those with `available_qty <= LOW_STOCK_THRESHOLD` (default: 10)

---

## Environment Variables

| Variable               | Default                                              | Description                          |
|------------------------|------------------------------------------------------|--------------------------------------|
| `DATABASE_URL`         | `postgresql://postgres:postgres@localhost:5432/ethara` | PostgreSQL connection string       |
| `LOW_STOCK_THRESHOLD`  | `10`                                                 | Threshold for low-stock dashboard    |

---

## Quick Test

```bash
# Health check
curl http://127.0.0.1:8000/health

# Dashboard summary
curl http://127.0.0.1:8000/dashboard
```
