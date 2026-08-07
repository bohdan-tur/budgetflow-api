from decimal import Decimal

import pytest
from rest_framework import status

from finance.models import Transfer
from finance.models.choices import Currency
from tests.factories import TransferFactory, WalletFactory

pytestmark = pytest.mark.django_db


def test_get_transfer_list(auth_client, transfer):
    response = auth_client.get("/api/transfers/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == transfer.id


def test_get_transfer_list_returns_only_user_transfers(auth_client, user):
    wallet1 = WalletFactory(user=user)
    wallet2 = WalletFactory(user=user)

    transfer = TransferFactory(
        from_wallet=wallet1,
        to_wallet=wallet2,
    )

    TransferFactory()

    response = auth_client.get("/api/transfers/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == transfer.id
    assert response.data[0]["from_wallet"] == wallet1.id
    assert response.data[0]["to_wallet"] == wallet2.id


def test_get_transfer_detail_other_user(auth_client):
    transfer = TransferFactory()

    response = auth_client.get(f"/api/transfers/{transfer.id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_transfer(auth_client, from_wallet, to_wallet):
    from_wallet.balance = Decimal("1000.00")
    from_wallet.save()

    to_wallet.balance = Decimal("500.00")
    to_wallet.save()

    from datetime import date

    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": to_wallet.id,
        "amount": 500,
        "transfer_date": date.today(),
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    transfer = Transfer.objects.first()

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["id"]
    assert response.data["from_wallet"] == from_wallet.id
    assert response.data["to_wallet"] == to_wallet.id
    assert response.data["amount"] == "500.00"

    assert Transfer.objects.count() == 1
    assert transfer.from_wallet == from_wallet
    assert transfer.to_wallet == to_wallet
    assert transfer.amount == Decimal("500.00")

    assert from_wallet.balance == Decimal("500.00")
    assert to_wallet.balance == Decimal("1000.00")


def test_create_transfer_invalid_data(auth_client):
    payload = {
        "amount": 500,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transfer_to_other_user_wallet(auth_client, user):
    from_wallet = WalletFactory(user=user, balance=1000)
    to_wallet = WalletFactory()

    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": to_wallet.id,
        "amount": 500,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unauthorized_get_transfers(api_client):
    response = api_client.get("/api/transfers/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_create_transfer(api_client):
    response = api_client.post(
        "/api/transfers/",
        {
            "amount": 500,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_transfer_insufficient_balance(
    auth_client,
    from_wallet,
    to_wallet,
):
    from_wallet.balance = Decimal("100.00")
    from_wallet.save()

    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": to_wallet.id,
        "amount": 500,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transfer_same_wallet(
    auth_client,
    from_wallet,
):
    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": from_wallet.id,
        "amount": 100,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transfer_between_different_currencies(
    auth_client,
    user,
):
    from_wallet = WalletFactory(
        user=user,
        currency=Currency.USD,
        balance=Decimal("1000.00"),
    )
    to_wallet = WalletFactory(
        user=user,
        currency=Currency.UAH,
    )

    response = auth_client.post(
        "/api/transfers/",
        {
            "from_wallet": from_wallet.id,
            "to_wallet": to_wallet.id,
            "amount": 100,
        },
        format="json",
    )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Transfer.objects.filter(
        from_wallet=from_wallet,
        to_wallet=to_wallet,
    ).exists()
    assert from_wallet.balance == Decimal("1000.00")
    assert to_wallet.balance == Decimal("1000.00")


def test_create_transfer_negative_amount(
    auth_client,
    from_wallet,
    to_wallet,
):
    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": to_wallet.id,
        "amount": -100,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_transfer_zero_amount(
    auth_client,
    from_wallet,
    to_wallet,
):
    payload = {
        "from_wallet": from_wallet.id,
        "to_wallet": to_wallet.id,
        "amount": 0,
    }

    response = auth_client.post(
        "/api/transfers/",
        payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
