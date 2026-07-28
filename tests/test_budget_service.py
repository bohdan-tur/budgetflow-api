from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from finance.models import Budget
from finance.models.choices import CategoryType
from finance.services.budget_service import BudgetService
from tests.factories import (
    BudgetFactory,
    CategoryFactory,
    TransactionFactory,
    WalletFactory,
)

pytestmark = pytest.mark.django_db


def test_create_budget(user, expense_category):
    budget = BudgetService.create(
        user=user,
        validated_data={
            "category": expense_category,
            "amount": Decimal("1000.00"),
            "start_date": timezone.localdate(),
            "end_date": timezone.localdate() + timedelta(days=30),
        },
    )

    assert Budget.objects.filter(id=budget.id).exists()
    assert budget.user == user
    assert budget.amount == Decimal("1000.00")


def test_update_budget(budget):
    updated = BudgetService.update(
        instance=budget,
        validated_data={
            "amount": Decimal("2500.00"),
        },
    )

    budget.refresh_from_db()

    assert updated.amount == Decimal("2500.00")
    assert budget.amount == Decimal("2500.00")


def test_destroy_budget(budget):
    BudgetService.destroy(instance=budget)

    assert Budget.objects.count() == 0


def test_get_spent_amount(user):
    wallet = WalletFactory(user=user)

    expense = CategoryFactory(
        user=user,
        type=CategoryType.EXPENSE,
    )

    budget = BudgetFactory(
        user=user,
        category=expense,
        amount=Decimal("1000.00"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("250.00"),
        transaction_date=budget.start_date,
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("350.00"),
        transaction_date=budget.start_date,
    )

    spent = BudgetService.get_spent_amount(
        budget=budget,
    )

    assert spent == Decimal("600.00")


def test_get_remaining_amount(user):
    wallet = WalletFactory(user=user)

    expense = CategoryFactory(
        user=user,
        type=CategoryType.EXPENSE,
    )

    budget = BudgetFactory(
        user=user,
        category=expense,
        amount=Decimal("1000.00"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("400.00"),
        transaction_date=budget.start_date,
    )

    remaining = BudgetService.get_remaining_amount(
        budget=budget,
    )

    assert remaining == Decimal("600.00")


def test_get_percentage_used(user):
    wallet = WalletFactory(user=user)

    expense = CategoryFactory(
        user=user,
        type=CategoryType.EXPENSE,
    )

    budget = BudgetFactory(
        user=user,
        category=expense,
        amount=Decimal("1000.00"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("250.00"),
        transaction_date=budget.start_date,
    )

    percentage = BudgetService.get_percentage_used(
        budget=budget,
    )

    assert percentage == Decimal("25.00")


def test_is_budget_exceeded(user):
    wallet = WalletFactory(user=user)

    expense = CategoryFactory(
        user=user,
        type=CategoryType.EXPENSE,
    )

    budget = BudgetFactory(
        user=user,
        category=expense,
        amount=Decimal("500.00"),
    )

    TransactionFactory(
        wallet=wallet,
        category=expense,
        amount=Decimal("600.00"),
        transaction_date=budget.start_date,
    )

    assert BudgetService.is_budget_exceeded(
        budget=budget,
    ) is True