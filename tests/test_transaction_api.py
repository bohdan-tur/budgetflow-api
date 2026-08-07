from decimal import Decimal

import pytest
from rest_framework import status

from finance.models import Transaction
from tests.factories import CategoryFactory, TransactionFactory, WalletFactory

pytestmark = pytest.mark.django_db


def test_get_transaction_list(auth_client, wallet, income_category):
    transaction = TransactionFactory(wallet=wallet, category=income_category)

    response = auth_client.get("/api/transactions/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == transaction.id


def test_get_transaction_list_returns_only_user_transactions(user, auth_client):
    wallet1 = WalletFactory(user=user)
    wallet2 = WalletFactory()
    category1 = CategoryFactory(user=user)
    category2 = CategoryFactory()

    transaction1 = TransactionFactory(wallet=wallet1, category=category1)
    TransactionFactory(wallet=wallet2, category=category2)

    response = auth_client.get("/api/transactions/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == transaction1.id
    assert response.data[0]["amount"] == str(transaction1.amount)


def test_get_transaction_detail(wallet, income_category, auth_client):
    transaction = TransactionFactory(wallet=wallet, category=income_category)

    response = auth_client.get(f"/api/transactions/{transaction.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == transaction.id
    assert response.data["amount"] == str(transaction.amount)


def test_get_transaction_detail_other_user(auth_client):
    wallet2 = WalletFactory()
    category2 = CategoryFactory(user=wallet2.user)

    transaction2 = TransactionFactory(
        wallet=wallet2,
        category=category2,
    )

    response = auth_client.get(f"/api/transactions/{transaction2.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_transaction_income(user, income_category, auth_client):
    wallet = WalletFactory(user=user, balance=500)

    data = {
        "wallet": wallet.id,
        "category": income_category.id,
        "amount": 100,
    }

    response = auth_client.post("/api/transactions/", data, format="json")

    wallet.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"]
    assert response.data["wallet"] == wallet.id
    assert Transaction.objects.count() == 1
    assert wallet.balance == Decimal("600.00")


def test_create_transaction_expense(user, auth_client, expense_category):
    wallet = WalletFactory(user=user, balance=500)

    data = {
        "wallet": wallet.id,
        "category": expense_category.id,
        "amount": 300,
    }

    response = auth_client.post("/api/transactions/", data, format="json")

    wallet.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"]
    assert response.data["wallet"] == wallet.id
    assert Transaction.objects.count() == 1
    assert wallet.balance == Decimal("200.00")


def test_create_transaction_expense_zero_balance(user, auth_client, expense_category):
    wallet = WalletFactory(user=user, balance=0)

    data = {
        "wallet": wallet.id,
        "category": expense_category.id,
        "amount": 300,
    }

    response = auth_client.post("/api/transactions/", data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transaction_unauthorized(api_client, income_category, wallet):
    data = {
        "wallet": wallet.id,
        "category": income_category.id,
        "amount": 100,
    }

    response = api_client.post("/api/transactions/", data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_transaction_invalid_data(auth_client):
    data = {"amount": 100}

    response = auth_client.post("/api/transactions/", data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_transaction_amount(auth_client, expense_category, user):
    wallet = WalletFactory(user=user, balance=500)

    data = {
        "wallet": wallet.id,
        "category": expense_category.id,
        "amount": 300,
    }

    response1 = auth_client.post("/api/transactions/", data, format="json")

    assert response1.status_code == status.HTTP_201_CREATED

    transaction_id = response1.data["id"]

    response2 = auth_client.patch(
        f"/api/transactions/{transaction_id}/",
        {"amount": 400},
        format="json",
    )

    wallet.refresh_from_db()
    transaction = Transaction.objects.get(id=transaction_id)

    assert response2.status_code == status.HTTP_200_OK
    assert wallet.balance == Decimal("100.00")
    assert transaction.amount == Decimal("400.00")


def test_update_transaction_category(
    expense_category,
    income_category,
    auth_client,
    wallet,
):
    data = {
        "wallet": wallet.id,
        "category": expense_category.id,
        "amount": 300,
    }

    response1 = auth_client.post("/api/transactions/", data, format="json")

    transaction_id = response1.data["id"]

    response2 = auth_client.patch(
        f"/api/transactions/{transaction_id}/",
        {"category": income_category.id},
        format="json",
    )

    transaction = Transaction.objects.get(id=transaction_id)

    assert response2.status_code == status.HTTP_200_OK
    assert transaction.category == income_category


def test_update_transaction_category_recalculates_balance(
    expense_category, income_category, user, auth_client
):

    wallet = WalletFactory(user=user, balance=1000)

    data = {"wallet": wallet.id, "category": expense_category.id, "amount": 300}

    response1 = auth_client.post("/api/transactions/", data, format="json")
    wallet.refresh_from_db()
    assert wallet.balance == Decimal("700.00")

    transaction_id = response1.data["id"]
    auth_client.patch(
        f"/api/transactions/{transaction_id}/",
        {"category": income_category.id},
        format="json",
    )

    wallet.refresh_from_db()

    assert wallet.balance == Decimal("1300.00")


def test_update_transaction_wallet(income_category, auth_client, user):
    wallet1 = WalletFactory(user=user, balance=500)
    wallet2 = WalletFactory(user=user, balance=800)

    data = {
        "wallet": wallet1.id,
        "category": income_category.id,
        "amount": 300,
    }

    response1 = auth_client.post("/api/transactions/", data, format="json")

    transaction_id = response1.data["id"]

    response2 = auth_client.patch(
        f"/api/transactions/{transaction_id}/",
        {"wallet": wallet2.id},
        format="json",
    )

    wallet1.refresh_from_db()
    wallet2.refresh_from_db()

    transaction = Transaction.objects.get(id=transaction_id)

    assert response2.status_code == status.HTTP_200_OK
    assert transaction.wallet == wallet2
    assert wallet1.balance == Decimal("500.00")
    assert wallet2.balance == Decimal("1100.00")


def test_update_other_user_transaction(auth_client):
    wallet = WalletFactory()
    category = CategoryFactory(user=wallet.user)

    transaction = TransactionFactory(
        wallet=wallet,
        category=category,
    )

    response = auth_client.patch(
        f"/api/transactions/{transaction.id}/",
        {"amount": 100},
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_transaction_invalid_data(auth_client, wallet, income_category):
    transaction = TransactionFactory(wallet=wallet, category=income_category)

    response = auth_client.patch(
        f"/api/transactions/{transaction.id}/", {"amount": -100}, format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("category_fixture", ["income_category", "expense_category"])
def test_delete_transaction(auth_client, wallet, category_fixture, request):
    category = request.getfixturevalue(category_fixture)

    data = {
        "wallet": wallet.id,
        "category": category.id,
        "amount": 300,
    }

    response1 = auth_client.post("/api/transactions/", data, format="json")

    transaction_id = response1.data["id"]

    response2 = auth_client.delete(f"/api/transactions/{transaction_id}/")

    wallet.refresh_from_db()

    assert response2.status_code == status.HTTP_204_NO_CONTENT
    assert wallet.balance == Decimal("1000.00")
    assert Transaction.objects.count() == 0


def test_delete_other_user_transaction(auth_client):
    wallet = WalletFactory()
    category = CategoryFactory(user=wallet.user)

    transaction = TransactionFactory(
        wallet=wallet,
        category=category,
    )

    response = auth_client.delete(f"/api/transactions/{transaction.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_transaction(auth_client):
    response = auth_client.delete("/api/transactions/99999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_transaction_with_other_user_wallet(auth_client, income_category):
    wallet = WalletFactory()

    payload = {
        "wallet": wallet.id,
        "category": income_category.id,
        "amount": 100,
    }

    response = auth_client.post(
        "/api/transactions/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transaction_with_other_user_category(auth_client, wallet):
    category = CategoryFactory()

    payload = {
        "wallet": wallet.id,
        "category": category.id,
        "amount": 100,
    }

    response = auth_client.post(
        "/api/transactions/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
