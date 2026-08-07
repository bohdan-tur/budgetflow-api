import pytest
from django.db.models.deletion import ProtectedError

from finance.models import Category, Wallet
from tests.factories import (
    BudgetFactory,
    CategoryFactory,
    TransactionFactory,
    WalletFactory,
)

pytestmark = pytest.mark.django_db


def test_wallet_with_transactions_is_protected_from_direct_deletion():
    wallet = WalletFactory()
    TransactionFactory(
        wallet=wallet,
        category=CategoryFactory(user=wallet.user),
    )

    with pytest.raises(ProtectedError):
        wallet.delete()

    assert Wallet.objects.filter(id=wallet.id).exists()
    assert wallet.transactions.exists()


def test_category_with_budgets_is_protected_from_direct_deletion():
    category = CategoryFactory()
    budget = BudgetFactory(
        user=category.user,
        category=category,
    )

    with pytest.raises(ProtectedError):
        category.delete()

    assert Category.objects.filter(id=category.id).exists()
    assert category.budgets.filter(id=budget.id).exists()
