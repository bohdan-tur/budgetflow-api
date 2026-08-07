import pytest
from rest_framework.test import APIClient

from finance.models.choices import CategoryType
from tests.factories import (
    BudgetFactory,
    CategoryFactory,
    TransactionFactory,
    TransferFactory,
    UserFactory,
    WalletFactory,
)


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def wallet(user):
    return WalletFactory(user=user)


@pytest.fixture
def income_category(user):
    return CategoryFactory(user=user, type=CategoryType.INCOME)


@pytest.fixture
def expense_category(user):
    return CategoryFactory(user=user, type=CategoryType.EXPENSE)


@pytest.fixture
def from_wallet(user):
    return WalletFactory(user=user)


@pytest.fixture
def to_wallet(user):
    return WalletFactory(user=user)


@pytest.fixture
def transaction(wallet, category):
    return TransactionFactory(wallet=wallet, category=category)


@pytest.fixture
def transfer(from_wallet, to_wallet):
    return TransferFactory(from_wallet=from_wallet, to_wallet=to_wallet)


@pytest.fixture
def budget(user, expense_category):
    return BudgetFactory(user=user, category=expense_category)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client
