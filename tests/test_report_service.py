from datetime import date
from decimal import Decimal

import pytest

from finance.models.choices import CategoryType
from finance.services.report_service import ReportService
from tests.factories import (
    CategoryFactory,
    TransactionFactory,
    WalletFactory,
)

pytestmark = pytest.mark.django_db


def test_get_total_income():
    wallet = WalletFactory()

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    TransactionFactory(
        wallet=wallet,
        category=income,
        amount=Decimal("1000"),
    )

    TransactionFactory(
        wallet=wallet,
        category=income,
        amount=Decimal("500"),
    )

    result = ReportService.get_total_income(
        user=wallet.user,
    )

    assert result == Decimal("1500")


def test_get_total_income_returns_zero():
    wallet = WalletFactory()

    result = ReportService.get_total_income(
        user=wallet.user,
    )

    assert result == Decimal("0.00")


def test_get_total_expense():
    wallet = WalletFactory()

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("200"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("300"),
    )

    result = ReportService.get_total_expense(
        user=wallet.user,
    )

    assert result == Decimal("500")


def test_get_total_expense_returns_zero():
    wallet = WalletFactory()

    result = ReportService.get_total_expense(
        user=wallet.user,
    )

    assert result == Decimal("0.00")


def test_get_current_balance():
    wallet = WalletFactory(
        balance=Decimal("2500"),
    )

    result = ReportService.get_current_balance(
        user=wallet.user,
    )

    assert result == Decimal("2500")


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
        "total_income": Decimal("1500"),
        "total_expense": Decimal("500"),
        "current_balance": Decimal("1000"),
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

    assert result["total_income"] == Decimal("1000")
    assert result["total_expense"] == Decimal("300")


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
    assert result[0]["income"] == Decimal("1000")
    assert result[0]["expense"] == Decimal("400")
