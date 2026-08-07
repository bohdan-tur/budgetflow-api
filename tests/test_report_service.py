from datetime import date
from decimal import Decimal

import pytest

from finance.models.choices import CategoryType, Currency
from finance.services.report_service import ReportService
from tests.factories import (
    CategoryFactory,
    TransactionFactory,
    WalletFactory,
)

pytestmark = pytest.mark.django_db


def test_get_summary():
    wallet = WalletFactory(
        balance=Decimal("1000"),
    )

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=income,
        amount=Decimal("1500"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("500"),
    )

    result = ReportService.get_summary(
        user=wallet.user,
    )

    assert result == {
        "currencies": [
            {
                "currency": Currency.UAH,
                "total_income": Decimal("1500"),
                "total_expense": Decimal("500"),
                "current_balance": Decimal("1000"),
            }
        ]
    }


def test_get_summary_separates_currencies():
    uah_wallet = WalletFactory(
        currency=Currency.UAH,
        balance=Decimal("1000"),
    )
    usd_wallet = WalletFactory(
        user=uah_wallet.user,
        currency=Currency.USD,
        balance=Decimal("200"),
    )
    income = CategoryFactory(
        user=uah_wallet.user,
        type=CategoryType.INCOME,
    )

    TransactionFactory(
        wallet=uah_wallet,
        category=income,
        amount=Decimal("500"),
    )
    TransactionFactory(
        wallet=usd_wallet,
        category=income,
        amount=Decimal("50"),
    )

    result = ReportService.get_summary(user=uah_wallet.user)

    assert result == {
        "currencies": [
            {
                "currency": Currency.UAH,
                "total_income": Decimal("500"),
                "total_expense": Decimal("0.00"),
                "current_balance": Decimal("1000"),
            },
            {
                "currency": Currency.USD,
                "total_income": Decimal("50"),
                "total_expense": Decimal("0.00"),
                "current_balance": Decimal("200"),
            },
        ]
    }


def test_get_income_by_category():
    wallet = WalletFactory()

    salary = CategoryFactory(
        user=wallet.user,
        name="Salary",
        type=CategoryType.INCOME,
    )

    TransactionFactory(
        wallet=wallet,
        category=salary,
        amount=Decimal("1000"),
    )

    TransactionFactory(
        wallet=wallet,
        category=salary,
        amount=Decimal("500"),
    )

    result = list(
        ReportService.get_income_by_category(
            user=wallet.user,
        )
    )

    assert result == [
        {
            "currency": Currency.UAH,
            "category_name": "Salary",
            "total": Decimal("1500.00"),
        }
    ]


def test_get_expenses_by_category():
    wallet = WalletFactory()

    food = CategoryFactory(
        user=wallet.user,
        name="Food",
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=food,
        amount=Decimal("200"),
    )

    TransactionFactory(
        wallet=wallet,
        category=food,
        amount=Decimal("300"),
    )

    result = list(
        ReportService.get_expenses_by_category(
            user=wallet.user,
        )
    )

    assert result == [
        {
            "currency": Currency.UAH,
            "category_name": "Food",
            "total": Decimal("500.00"),
        }
    ]


def test_get_top_expense_categories():
    wallet = WalletFactory()

    food = CategoryFactory(
        user=wallet.user,
        name="Food",
        type=CategoryType.EXPENSE,
    )

    transport = CategoryFactory(
        user=wallet.user,
        name="Transport",
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=food,
        amount=Decimal("1000"),
    )

    TransactionFactory(
        wallet=wallet,
        category=transport,
        amount=Decimal("300"),
    )

    result = list(
        ReportService.get_top_expense_categories(
            user=wallet.user,
        )
    )

    assert result[0]["category_name"] == "Food"
    assert result[0]["currency"] == Currency.UAH
    assert result[0]["total"] == Decimal("1000.00")

    assert result[1]["category_name"] == "Transport"
    assert result[1]["total"] == Decimal("300.00")


def test_get_statistics_by_period():
    wallet = WalletFactory()

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=income,
        amount=Decimal("1000"),
        transaction_date=date(2026, 7, 10),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("300"),
        transaction_date=date(2026, 7, 11),
    )

    result = ReportService.get_statistics_by_period(
        user=wallet.user,
        start_time=date(2026, 7, 1),
        end_time=date(2026, 7, 31),
    )

    assert result["currencies"] == [
        {
            "currency": Currency.UAH,
            "total_income": Decimal("1000"),
            "total_expense": Decimal("300"),
        }
    ]


def test_get_monthly_statistics():
    wallet = WalletFactory()

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=income,
        amount=Decimal("1000"),
        transaction_date=date(2026, 7, 10),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("400"),
        transaction_date=date(2026, 7, 15),
    )

    result = list(
        ReportService.get_monthly_statistics(
            user=wallet.user,
        )
    )

    assert len(result) == 1
    assert result[0]["currency"] == Currency.UAH
    assert result[0]["income"] == Decimal("1000")
    assert result[0]["expense"] == Decimal("400")


def test_category_report_separates_currencies():
    uah_wallet = WalletFactory(currency=Currency.UAH)
    usd_wallet = WalletFactory(
        user=uah_wallet.user,
        currency=Currency.USD,
    )
    expense = CategoryFactory(
        user=uah_wallet.user,
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=uah_wallet,
        category=expense,
        amount=Decimal("1000"),
    )
    TransactionFactory(
        wallet=usd_wallet,
        category=expense,
        amount=Decimal("100"),
    )

    result = list(ReportService.get_expenses_by_category(user=uah_wallet.user))

    assert [item["currency"] for item in result] == [Currency.UAH, Currency.USD]
    assert [item["total"] for item in result] == [
        Decimal("1000"),
        Decimal("100"),
    ]


def test_period_statistics_separates_currencies():
    uah_wallet = WalletFactory(currency=Currency.UAH)
    usd_wallet = WalletFactory(
        user=uah_wallet.user,
        currency=Currency.USD,
    )
    income = CategoryFactory(
        user=uah_wallet.user,
        type=CategoryType.INCOME,
    )

    TransactionFactory(
        wallet=uah_wallet,
        category=income,
        amount=Decimal("1000"),
    )
    TransactionFactory(
        wallet=usd_wallet,
        category=income,
        amount=Decimal("100"),
    )

    result = ReportService.get_statistics_by_period(user=uah_wallet.user)

    assert [item["currency"] for item in result["currencies"]] == [
        Currency.UAH,
        Currency.USD,
    ]
    assert [item["total_income"] for item in result["currencies"]] == [
        Decimal("1000"),
        Decimal("100"),
    ]


def test_monthly_statistics_separates_currencies():
    uah_wallet = WalletFactory(currency=Currency.UAH)
    usd_wallet = WalletFactory(
        user=uah_wallet.user,
        currency=Currency.USD,
    )
    income = CategoryFactory(
        user=uah_wallet.user,
        type=CategoryType.INCOME,
    )

    TransactionFactory(
        wallet=uah_wallet,
        category=income,
        amount=Decimal("1000"),
        transaction_date=date(2026, 7, 10),
    )
    TransactionFactory(
        wallet=usd_wallet,
        category=income,
        amount=Decimal("100"),
        transaction_date=date(2026, 7, 10),
    )

    result = list(ReportService.get_monthly_statistics(user=uah_wallet.user))

    assert [item["currency"] for item in result] == [Currency.UAH, Currency.USD]
    assert [item["income"] for item in result] == [
        Decimal("1000"),
        Decimal("100"),
    ]


def test_top_expense_limit_is_applied_per_currency():
    uah_wallet = WalletFactory(currency=Currency.UAH)
    usd_wallet = WalletFactory(
        user=uah_wallet.user,
        currency=Currency.USD,
    )

    for wallet, prefix in ((uah_wallet, "UAH"), (usd_wallet, "USD")):
        for index, amount in enumerate((Decimal("200"), Decimal("100"))):
            category = CategoryFactory(
                user=uah_wallet.user,
                name=f"{prefix} category {index}",
                type=CategoryType.EXPENSE,
            )
            TransactionFactory(
                wallet=wallet,
                category=category,
                amount=amount,
            )

    result = ReportService.get_top_expense_categories(
        user=uah_wallet.user,
        limit=1,
    )

    assert len(result) == 2
    assert [item["currency"] for item in result] == [Currency.UAH, Currency.USD]
    assert [item["total"] for item in result] == [
        Decimal("200"),
        Decimal("200"),
    ]
