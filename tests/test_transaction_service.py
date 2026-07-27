from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from finance.models import Transaction
from finance.services.transaction_service import TransactionService
from tests.factories import (
    WalletFactory,
    CategoryFactory,
)

from finance.models.choices import CategoryType

pytestmark = pytest.mark.django_db




def test_create_income_transaction():
    wallet = WalletFactory(
        balance=Decimal("100.00"),
    )

    category = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    transaction = TransactionService.create(
        validated_data={
            "wallet": wallet,
            "category": category,
            "amount": Decimal("500.00"),
            "description": "Salary",
        }
    )

    wallet.refresh_from_db()

    assert Transaction.objects.count() == 1
    assert transaction.amount == Decimal("500.00")
    assert wallet.balance == Decimal("600.00")


def test_create_expense_transaction():
    wallet = WalletFactory(
        balance=Decimal("1000.00"),
    )

    category = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    transaction = TransactionService.create(
        validated_data={
            "wallet": wallet,
            "category": category,
            "amount": Decimal("250.00"),
            "description": "Food",
        }
    )

    wallet.refresh_from_db()

    assert Transaction.objects.count() == 1
    assert transaction.amount == Decimal("250.00")
    assert wallet.balance == Decimal("750.00")




def test_create_expense_with_insufficient_funds():
    wallet = WalletFactory(
        balance=Decimal("100.00"),
    )

    category = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    with pytest.raises(ValidationError):
        TransactionService.create(
            validated_data={
                "wallet": wallet,
                "category": category,
                "amount": Decimal("200.00"),
                "description": "Food",
            }
        )

    wallet.refresh_from_db()

    assert Transaction.objects.count() == 0
    assert wallet.balance == Decimal("100.00")



def test_update_income_amount():
    wallet = WalletFactory(
        balance=Decimal("1500.00"),
    )

    category = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=category,
        amount=Decimal("500.00"),
        description="Salary",
    )

    validated_data = {
        "amount": Decimal("800.00"),
    }

    updated = TransactionService.update(
        instance=transaction,
        validated_data=validated_data,
    )

    wallet.refresh_from_db()

    assert updated.amount == Decimal("800.00")
    assert wallet.balance == Decimal("1800.00")




def test_update_transaction_change_income_to_expense():
    wallet = WalletFactory(
        balance=Decimal("1500.00"),
    )

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=income,
        amount=Decimal("500.00"),
        description="Salary",
    )

    updated = TransactionService.update(
        instance=transaction,
        validated_data={
            "category": expense,
        },
    )

    wallet.refresh_from_db()

    assert updated.category == expense
    assert wallet.balance == Decimal("500.00")


def test_update_transaction_change_wallet():
    wallet1 = WalletFactory(
        balance=Decimal("1500.00"),
    )

    wallet2 = WalletFactory(
        user=wallet1.user,
        balance=Decimal("1000.00"),
    )

    income = CategoryFactory(
        user=wallet1.user,
        type=CategoryType.INCOME,
    )

    transaction = Transaction.objects.create(
        wallet=wallet1,
        category=income,
        amount=Decimal("500.00"),
        description="Salary",
    )

    updated = TransactionService.update(
        instance=transaction,
        validated_data={
            "wallet": wallet2,
        },
    )

    wallet1.refresh_from_db()
    wallet2.refresh_from_db()

    assert updated.wallet == wallet2
    assert wallet1.balance == Decimal("1000.00")
    assert wallet2.balance == Decimal("1500.00")



def test_destroy_income_transaction():
    wallet = WalletFactory(
        balance=Decimal("1500.00"),
    )

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=income,
        amount=Decimal("500.00"),
    )

    TransactionService.destroy(
        instance=transaction,
    )

    wallet.refresh_from_db()

    assert wallet.balance == Decimal("1000.00")
    assert Transaction.objects.count() == 0



def test_destroy_expense_transaction():
    wallet = WalletFactory(
        balance=Decimal("500.00"),
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=expense,
        amount=Decimal("500.00"),
    )

    TransactionService.destroy(
        instance=transaction,
    )

    wallet.refresh_from_db()

    assert wallet.balance == Decimal("1000.00")
    assert Transaction.objects.count() == 0



def test_update_transaction_change_expense_to_income():
    wallet = WalletFactory(
        balance=Decimal("500.00"),
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    income = CategoryFactory(
        user=wallet.user,
        type=CategoryType.INCOME,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=expense,
        amount=Decimal("500.00"),
    )

    updated = TransactionService.update(
        instance=transaction,
        validated_data={
            "category": income,
        },
    )

    wallet.refresh_from_db()

    assert updated.category == income
    assert wallet.balance == Decimal("1500.00")




def test_update_expense_amount():
    wallet = WalletFactory(
        balance=Decimal("500.00"),
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=expense,
        amount=Decimal("500.00"),
    )

    updated = TransactionService.update(
        instance=transaction,
        validated_data={
            "amount": Decimal("800.00"),
        },
    )

    wallet.refresh_from_db()

    assert updated.amount == Decimal("800.00")
    assert wallet.balance == Decimal("200.00")



def test_update_expense_insufficient_funds():
    wallet = WalletFactory(
        balance=Decimal("100.00"),
    )

    expense = CategoryFactory(
        user=wallet.user,
        type=CategoryType.EXPENSE,
    )

    transaction = Transaction.objects.create(
        wallet=wallet,
        category=expense,
        amount=Decimal("100.00"),
    )

    with pytest.raises(ValidationError):
        TransactionService.update(
            instance=transaction,
            validated_data={
                "amount": Decimal("300.00"),
            },
        )

    wallet.refresh_from_db()

    assert wallet.balance == Decimal("100.00")