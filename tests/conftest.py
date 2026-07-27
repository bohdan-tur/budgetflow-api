from decimal import Decimal

import pytest

from finance.models import Category, Wallet
from finance.models.choices import CategoryType, Currency
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
    )


@pytest.fixture
def wallet(user):
    return Wallet.objects.create(
        user=user,
        name="Main Wallet",
        currency=Currency.UAH,
        balance=Decimal("1000.00"),
    )


@pytest.fixture
def income_category(user):
    return Category.objects.create(
        user=user,
        name="Salary",
        type=CategoryType.INCOME,
    )


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        user=user,
        name="Food",
        type=CategoryType.EXPENSE,
    )