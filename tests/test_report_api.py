from datetime import date

import pytest
from rest_framework import status

from finance.models.choices import CategoryType, Currency
from tests.factories import CategoryFactory, TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db


def test_get_monthly_report(auth_client, user, income_category, expense_category):
    wallet = WalletFactory(user=user)

    TransactionFactory(
        wallet=wallet,
        category=income_category,
        amount=100,
    )

    TransactionFactory(
        wallet=wallet,
        category=expense_category,
        amount=50,
    )
    response = auth_client.get("/api/reports/monthly_statistics/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    report = response.data[0]

    assert report["currency"] == Currency.UAH
    assert report["income"] == "100.00"
    assert report["expense"] == "50.00"


def test_get_monthly_report_unauthorized(api_client):
    response = api_client.get("/api/reports/monthly_statistics/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_statistics_by_period_with_valid_dates(
    auth_client,
    user,
    income_category,
):
    wallet = WalletFactory(user=user)
    TransactionFactory(
        wallet=wallet,
        category=income_category,
        amount=100,
        transaction_date=date(2026, 8, 1),
    )

    response = auth_client.get(
        "/api/reports/statistics_by_period/",
        {
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["currencies"] == [
        {
            "currency": Currency.UAH,
            "total_income": "100.00",
            "total_expense": "0.00",
        }
    ]


def test_get_statistics_by_period_with_invalid_date(auth_client):
    response = auth_client.get(
        "/api/reports/statistics_by_period/",
        {
            "start_date": "not-a-date",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_statistics_by_period_with_reversed_dates(auth_client):
    response = auth_client.get(
        "/api/reports/statistics_by_period/",
        {
            "start_date": "2026-08-31",
            "end_date": "2026-08-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_top_expense_categories_with_limit(auth_client, user):
    wallet = WalletFactory(user=user)

    for name, amount in (("Food", 200), ("Transport", 100)):
        category = CategoryFactory(
            user=user,
            name=name,
            type=CategoryType.EXPENSE,
        )
        TransactionFactory(
            wallet=wallet,
            category=category,
            amount=amount,
        )

    response = auth_client.get(
        "/api/reports/top_expense_categories/",
        {
            "limit": 1,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["currency"] == Currency.UAH
    assert response.data[0]["category_name"] == "Food"


@pytest.mark.parametrize("invalid_limit", ["invalid", 0, -1, 101])
def test_get_top_expense_categories_with_invalid_limit(
    auth_client,
    invalid_limit,
):
    response = auth_client.get(
        "/api/reports/top_expense_categories/",
        {
            "limit": invalid_limit,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_summary_separates_currencies(auth_client, user, income_category):
    uah_wallet = WalletFactory(
        user=user,
        currency=Currency.UAH,
        balance=1000,
    )
    usd_wallet = WalletFactory(
        user=user,
        currency=Currency.USD,
        balance=200,
    )
    TransactionFactory(
        wallet=uah_wallet,
        category=income_category,
        amount=500,
    )
    TransactionFactory(
        wallet=usd_wallet,
        category=income_category,
        amount=50,
    )

    response = auth_client.get("/api/reports/summary/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["currencies"] == [
        {
            "currency": Currency.UAH,
            "total_income": "500.00",
            "total_expense": "0.00",
            "current_balance": "1000.00",
        },
        {
            "currency": Currency.USD,
            "total_income": "50.00",
            "total_expense": "0.00",
            "current_balance": "200.00",
        },
    ]
