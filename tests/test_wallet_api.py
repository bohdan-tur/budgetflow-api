import pytest
from rest_framework import status

from finance.models import Wallet
from tests.factories import (
    CategoryFactory,
    TransactionFactory,
    TransferFactory,
    WalletFactory,
)

pytestmark = pytest.mark.django_db


def test_get_wallet_list(auth_client, wallet):
    response = auth_client.get("/api/wallets/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == wallet.id


def test_get_wallet_list_returns_only_user_wallets(auth_client, user):
    WalletFactory(user=user)
    WalletFactory()

    response = auth_client.get("/api/wallets/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


def test_get_wallet_detail(auth_client, wallet):
    response = auth_client.get(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == wallet.id
    assert response.data["name"] == wallet.name


def test_get_wallet_detail_other_user(auth_client):
    wallet = WalletFactory()

    response = auth_client.get(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_wallet(auth_client):
    payload = {
        "name": "New Wallet",
        "currency": "USD",
    }

    response = auth_client.post(
        "/api/wallets/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "New Wallet"
    assert response.data["currency"] == "USD"
    assert response.data["balance"] == "0.00"


def test_create_wallet_invalid_data(auth_client):
    payload = {
        "currency": "USD",
    }

    response = auth_client.post(
        "/api/wallets/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_wallet(auth_client, wallet):
    payload = {
        "name": "Updated Wallet",
    }

    response = auth_client.patch(
        f"/api/wallets/{wallet.id}/",
        payload,
        format="json",
    )

    wallet.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert wallet.name == "Updated Wallet"


def test_update_other_user_wallet(auth_client):
    wallet = WalletFactory()

    response = auth_client.patch(
        f"/api/wallets/{wallet.id}/",
        {
            "name": "Hack",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_wallet(auth_client, wallet):
    response = auth_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_wallet_with_transaction(auth_client, wallet):
    TransactionFactory(
        wallet=wallet,
        category=CategoryFactory(user=wallet.user),
    )

    response = auth_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Wallet.objects.filter(id=wallet.id).exists()


def test_delete_wallet_with_outgoing_transfer(auth_client, wallet):
    TransferFactory(
        from_wallet=wallet,
        to_wallet=WalletFactory(user=wallet.user),
    )

    response = auth_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Wallet.objects.filter(id=wallet.id).exists()


def test_delete_wallet_with_incoming_transfer(auth_client, wallet):
    TransferFactory(
        from_wallet=WalletFactory(user=wallet.user),
        to_wallet=wallet,
    )

    response = auth_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Wallet.objects.filter(id=wallet.id).exists()


def test_delete_other_user_wallet(auth_client):
    wallet = WalletFactory()

    response = auth_client.delete(f"/api/wallets/{wallet.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unauthorized_get_wallets(api_client):
    response = api_client.get("/api/wallets/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_create_wallet(api_client):
    response = api_client.post(
        "/api/wallets/",
        {
            "name": "Wallet",
            "currency": "USD",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
