# BudgetFlow API

[![CI](https://github.com/bohdan-tur/budgetflow-api/actions/workflows/ci.yaml/badge.svg)](https://github.com/bohdan-tur/budgetflow-api/actions/workflows/ci.yaml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.17-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

A personal-finance REST API built with Django REST Framework. BudgetFlow
supports multiple wallets and currencies, income and expense tracking,
wallet-to-wallet transfers, category budgets, and currency-aware reports.

The project emphasizes correctness in financial workflows: strict user data
isolation, decimal arithmetic, atomic balance updates, row-level locking, and
business-rule verification through automated tests.

## Highlights

- JWT authentication with rotating and blacklisted refresh tokens.
- User-owned wallets in `UAH`, `USD`, and `EUR`.
- Income and expense transactions with automatic balance recalculation.
- Atomic same-currency transfers between wallets.
- Category budgets with calculated spending progress.
- Reports grouped by currency, category, month, and date range.
- Protection against cross-user access and deletion of financial history.
- Dockerized PostgreSQL environment and GitHub Actions verification.

## Financial integrity

- Monetary values use `Decimal`, never binary floating point.
- Expenses cannot reduce a wallet balance below zero.
- Balance-changing operations run inside database transactions.
- Wallet rows are locked while balances are updated to prevent races.
- Transfers require two wallets owned by the same user and using the same
  currency.
- Wallet currency becomes immutable after creation.
- Budgets can reference only expense categories.
- A category type cannot change after the category is used.
- Wallets and categories with financial history cannot be deleted.
- Reports never add values expressed in different currencies.

## Architecture

Money-changing operations are kept outside the HTTP layer and implemented as
services:

```text
HTTP request
    |
    v
ViewSet -------- authentication and user-scoped queryset
    |
    v
Serializer ----- input validation and response formatting
    |
    v
Service -------- business rules, atomic operations, row locking
    |
    v
Django ORM ----- PostgreSQL
```

This keeps serializers focused on API contracts while services own balance
changes, transfers, budgets, and reporting logic.

## Tech stack

| Area | Technologies |
|---|---|
| API | Python 3.12, Django 5.2, Django REST Framework |
| Authentication | Simple JWT |
| Persistence | PostgreSQL 16, Django ORM |
| Testing | Pytest, pytest-django, Factory Boy, coverage.py |
| Quality and CI | Ruff, Django system checks, GitHub Actions |
| Infrastructure | Docker, Docker Compose |

## Quick start

### Prerequisites

- Git
- Docker Engine or Docker Desktop with Docker Compose

### 1. Clone and configure

```bash
git clone https://github.com/bohdan-tur/budgetflow-api.git
cd budgetflow-api
cp .env.example .env
```

PowerShell equivalent:

```powershell
Copy-Item .env.example .env
```

Replace the placeholder `SECRET_KEY` and `DB_PASSWORD` values in `.env`.

### 2. Start the application

```bash
docker compose up --build
```

Compose waits for PostgreSQL, applies Django migrations, and starts the API.

| Service | Address |
|---|---|
| API | <http://localhost:8000/api/> |
| PostgreSQL | `localhost:5435` |

Stop the containers without deleting database data:

```bash
docker compose down
```

## Configuration

The repository includes a safe-to-commit [`.env.example`](.env.example). The
real `.env` file is ignored by Git.

| Variable | Purpose | Development example |
|---|---|---|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Cryptographic signing key | replace the placeholder |
| `ALLOWED_HOSTS` | Comma-separated accepted hosts | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database | `finance_tracker` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `change-me` |
| `DB_HOST` | Database host outside Docker | `localhost` |
| `DB_PORT` | Database port outside Docker | `5435` |
| `ACCESS_TOKEN_MINUTES` | Access-token lifetime | `15` |
| `REFRESH_TOKEN_DAYS` | Refresh-token lifetime | `7` |

The application fails at startup if `SECRET_KEY` is missing instead of falling
back to an unsafe value.

## Authentication

Registration and token endpoints are public. All finance resources require a
Bearer access token.

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "StrongPassword123!"
  }'
```

Registration returns the user together with access and refresh tokens. Use the
access token on protected endpoints:

```text
Authorization: Bearer <access-token>
```

Refresh with `POST /api/auth/token/refresh/`. Rotation returns a new token pair
and blacklists the submitted refresh token so it cannot be reused.

## API overview

Base URL: `/api/`

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register/` | Register and receive JWT tokens |
| `POST` | `/auth/token/` | Obtain access and refresh tokens |
| `POST` | `/auth/token/refresh/` | Rotate the refresh token |

### Finance resources

| Resource | Endpoint | Supported operations |
|---|---|---|
| Wallets | `/wallets/` | List, create, retrieve, rename, delete when empty |
| Categories | `/categories/` | CRUD with history protection |
| Transactions | `/transactions/` | CRUD with balance recalculation |
| Transfers | `/transfers/` | Create, list, retrieve |
| Budgets | `/budgets/` | CRUD for expense categories |

### Reports

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/reports/summary/` | Income, expenses, and balances by currency |
| `GET` | `/reports/expenses_by_category/` | Expenses by category and currency |
| `GET` | `/reports/income_by_category/` | Income by category and currency |
| `GET` | `/reports/monthly_statistics/` | Monthly totals by currency |
| `GET` | `/reports/statistics_by_period/` | Totals for an optional date range |
| `GET` | `/reports/top_expense_categories/` | Top expense categories per currency |

Example filters:

```http
GET /api/reports/statistics_by_period/?start_date=2026-01-01&end_date=2026-01-31
GET /api/reports/top_expense_categories/?limit=3
```

Reports preserve currency boundaries:

```json
{
  "currencies": [
    {
      "currency": "UAH",
      "total_income": "30000.00",
      "total_expense": "12500.00",
      "current_balance": "17500.00"
    },
    {
      "currency": "USD",
      "total_income": "1000.00",
      "total_expense": "250.00",
      "current_balance": "750.00"
    }
  ]
}
```

## Example transaction

```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": 1,
    "category": 1,
    "amount": "30000.00",
    "description": "Monthly salary",
    "transaction_date": "2026-08-07"
  }'
```

Income increases the wallet balance. Expenses first validate sufficient funds.
The transaction record and resulting wallet balance are committed atomically.

## Testing and quality

Run the complete suite in Docker:

```bash
docker compose run --rm web python -m pytest
```

Current result: **135 passing tests with 92% total coverage**. The suite covers authentication
boundaries, balance recalculation, insufficient funds, cross-user access,
currency rules, budgets, reports, and protected deletion.

Run line and branch coverage:

```bash
docker compose run --rm web coverage run -m pytest
docker compose run --rm web coverage report
```

CI reports current coverage alongside the PostgreSQL-backed test run. Local quality checks:

```bash
ruff check .
ruff format --check .
python manage.py check
```

GitHub Actions runs Ruff, Django system checks, and the PostgreSQL-backed test
suite on configured pushes and pull requests.

## Project structure

```text
budgetflow-api/
|-- api/                     # API router
|-- config/                  # Django settings and entry points
|-- finance/
|   |-- migrations/          # Schema history
|   |-- models/              # Financial entities
|   |-- serializers/         # API validation and representation
|   |-- services/            # Atomic operations and reports
|   `-- views/               # DRF viewsets
|-- users/                   # Custom user and registration
|-- tests/                   # Service and endpoint tests
|-- .github/workflows/       # Continuous integration
|-- docker-compose.yaml
|-- Dockerfile
|-- .env.example
`-- manage.py
```

## Author

**Bohdan Turevych**

- GitHub: [@bohdan-tur](https://github.com/bohdan-tur)
- LinkedIn: [Bohdan Turevych](https://www.linkedin.com/in/bohdan-turevych)

