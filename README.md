# BudgetFlow API

[![CI](https://github.com/bohdan-tur/budgetflow-api/actions/workflows/ci.yaml/badge.svg)](https://github.com/bohdan-tur/budgetflow-api/actions/workflows/ci.yaml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.17-A30000?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

A REST API for personal finance management, built with Django REST Framework.
It supports multiple wallets and currencies, income and expense tracking,
wallet-to-wallet transfers, category budgets, and currency-aware financial
reports.

The project focuses on backend fundamentals that matter in financial software:
data isolation, decimal arithmetic, atomic balance updates, row locking,
validation of business rules, and automated testing.

> **Status:** actively developed portfolio project.

## Table of contents

- [Features](#features)
- [Key business rules](#key-business-rules)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [Quick start with Docker](#quick-start-with-docker)
- [Environment variables](#environment-variables)
- [Authentication](#authentication)
- [API overview](#api-overview)
- [Example workflow](#example-workflow)
- [Testing and code quality](#testing-and-code-quality)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)

## Features

- JWT registration and authentication.
- User-owned wallets in `UAH`, `USD`, and `EUR`.
- Income and expense categories.
- Transactions that automatically update wallet balances.
- Atomic transfers between wallets of the same currency.
- Category budgets with calculated spending progress.
- Reports grouped by currency, category, month, and date range.
- Protection against accessing another user's financial data.
- Protection against deleting resources that contain financial history.
- Dockerized local environment with PostgreSQL health checks.
- GitHub Actions pipeline for linting, Django checks, and tests.

## Key business rules

The API enforces several rules to keep financial data consistent:

- Monetary values use `Decimal`, not floating-point numbers.
- An expense cannot make a wallet balance negative.
- Balance-changing operations run inside database transactions.
- Wallet rows are locked during balance updates to prevent race conditions.
- Transfers are allowed only between wallets owned by the same user and using
  the same currency.
- A wallet's currency cannot be changed after creation.
- Budgets can be created only for expense categories.
- A category type cannot change after the category is used by a transaction or
  budget.
- Wallets and categories containing financial history cannot be deleted.
- Reports never add amounts expressed in different currencies together.

## Tech stack

| Area | Technology |
| --- | --- |
| Language | Python 3.12 |
| Web framework | Django 5.2 |
| API | Django REST Framework |
| Authentication | Simple JWT |
| Database | PostgreSQL 16 |
| Testing | Pytest, pytest-django, Factory Boy |
| Code quality | Ruff |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |

## Architecture

Money-changing operations are separated from the HTTP layer and implemented in
services:

```text
HTTP request
    │
    ▼
ViewSet ── authentication and user-scoped queryset
    │
    ▼
Serializer ── input validation and response formatting
    │
    ▼
Service ── business rules, atomic operations, row locking
    │
    ▼
Django ORM ── PostgreSQL
```

This keeps serializers focused on API validation while services handle balance
changes and reporting logic.

## Quick start with Docker

### Prerequisites

- Git
- Docker Desktop or Docker Engine with Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/bohdan-tur/budgetflow-api.git
cd budgetflow-api
```

### 2. Create the environment file

Linux/macOS:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Replace the placeholder values in `.env`, especially `SECRET_KEY` and
`DB_PASSWORD`.

### 3. Build and start the application

```bash
docker compose up --build
```

Docker Compose waits for PostgreSQL, applies migrations, and starts Django.
The API is then available at:

```text
http://localhost:8000/api/
```

PostgreSQL is exposed locally on port `5435`.

To stop the application without deleting database data:

```bash
docker compose down
```

## Environment variables

The repository contains a safe-to-commit `.env.example`. The real `.env` is
ignored by Git.

| Variable | Purpose | Example |
| --- | --- | --- |
| `DEBUG` | Enables Django debug mode | `True` |
| `SECRET_KEY` | Django cryptographic signing key | replace the placeholder |
| `ALLOWED_HOSTS` | Comma-separated accepted hosts | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `finance_tracker` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `change-me` |
| `DB_HOST` | Database host outside Docker | `localhost` |
| `DB_PORT` | Database port outside Docker | `5435` |
| `ACCESS_TOKEN_MINUTES` | JWT access token lifetime | `15` |
| `REFRESH_TOKEN_DAYS` | JWT refresh token lifetime | `7` |

`SECRET_KEY` is required. The application fails at startup instead of using an
unsafe fallback value when it is missing.

## Authentication

All finance endpoints require a Bearer access token. Registration and token
endpoints are public.

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

Registration returns user information together with access and refresh tokens.

### Obtain a new token pair

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "StrongPassword123!"
  }'
```

Use the access token for protected endpoints:

```text
Authorization: Bearer <access-token>
```

Refresh an expired access token with:

```http
POST /api/auth/token/refresh/
```

Send the current refresh token in the request body:

```json
{
  "refresh": "<refresh-token>"
}
```

The response contains a new access token and a rotated refresh token. The
submitted refresh token is blacklisted and cannot be reused.

## API overview

Base URL:

```text
/api/
```

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register/` | Register a user and receive JWT tokens |
| `POST` | `/auth/token/` | Obtain access and refresh tokens |
| `POST` | `/auth/token/refresh/` | Rotate the refresh token and issue a new token pair |

### Finance resources

| Resource | Endpoints | Supported operations |
| --- | --- | --- |
| Wallets | `/wallets/`, `/wallets/{id}/` | List, create, retrieve, rename, delete empty wallet |
| Categories | `/categories/`, `/categories/{id}/` | Full CRUD with history protection |
| Transactions | `/transactions/`, `/transactions/{id}/` | Full CRUD with balance recalculation |
| Transfers | `/transfers/`, `/transfers/{id}/` | Create, list, retrieve |
| Budgets | `/budgets/`, `/budgets/{id}/` | Full CRUD for expense categories |

### Reports

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/reports/summary/` | Income, expenses, and balances grouped by currency |
| `GET` | `/reports/expenses_by_category/` | Expense totals by category and currency |
| `GET` | `/reports/income_by_category/` | Income totals by category and currency |
| `GET` | `/reports/monthly_statistics/` | Monthly income and expenses by currency |
| `GET` | `/reports/statistics_by_period/` | Totals for an optional date range |
| `GET` | `/reports/top_expense_categories/` | Top expense categories per currency |

Date range example:

```http
GET /api/reports/statistics_by_period/?start_date=2026-01-01&end_date=2026-01-31
```

Top categories accept a `limit` from `1` to `100`:

```http
GET /api/reports/top_expense_categories/?limit=3
```

Example summary response:

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

## Example workflow

### Create a wallet

```bash
curl -X POST http://localhost:8000/api/wallets/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main card",
    "currency": "UAH"
  }'
```

### Create an income category

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer <access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Salary",
    "type": "INCOME"
  }'
```

### Record the first income

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

Income increases the wallet balance. Expense transactions validate the
available balance before updating it. Both operations update the transaction
and wallet inside the same database transaction.

## Testing and code quality

Run the complete test suite in Docker:

```bash
docker compose run --rm web python -m pytest
```

The current suite contains **135 passing tests** covering services and API
endpoints, including authentication boundaries, balance recalculation,
insufficient funds, cross-user access, currency rules, budgets, reports, and
protected deletion.

Measure line and branch coverage with `coverage.py`:

```bash
docker compose run --rm web coverage run -m pytest
docker compose run --rm web coverage report
```

Generate a detailed HTML report:

```bash
docker compose run --rm web coverage html
```

Open `htmlcov/index.html` in a browser to inspect covered and missing lines.
CI requires at least **85%** total coverage.

Run Ruff locally:

```bash
ruff check .
ruff format --check .
```

GitHub Actions runs Ruff, Django system checks, and Pytest against a PostgreSQL
service on every pull request to `main`.

## Project structure

```text
budgetflow-api/
├── api/                     # API router
├── config/                  # Django settings and application entry points
├── finance/
│   ├── migrations/          # Database schema history
│   ├── models/              # Wallets, categories, transactions, transfers, budgets
│   ├── serializers/         # Request validation and response schemas
│   ├── services/            # Balance operations, transfers, budgets, reports
│   └── views/               # DRF viewsets
├── users/                   # Custom user and JWT registration
├── tests/
│   ├── factories/           # Factory Boy test data
│   ├── test_*_api.py        # Endpoint tests
│   └── test_*_service.py    # Business-logic tests
├── .github/workflows/       # Continuous integration
├── docker-compose.yaml
├── Dockerfile
└── manage.py
```

## Roadmap

- OpenAPI schema and Swagger/ReDoc documentation.
- Filtering, ordering, and pagination for resource lists.
- Optional exchange-rate support for cross-currency transfers.
- Recurring transactions and scheduled payments.
- Password reset, email verification, and refresh-token revocation.
- Deployment configuration and hosted demo.

## Author

Created by [bohdan-tur](https://github.com/bohdan-tur) as a backend portfolio
project.
