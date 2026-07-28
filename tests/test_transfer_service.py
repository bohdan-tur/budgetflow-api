from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from finance.models import Transfer
from finance.services.transfer_service import TransferService
from tests.factories import WalletFactory

pytestmark = pytest.mark.django_db


def test_create_transfer():
    from_wallet = WalletFactory(
        balance=Decimal("1000.00"),
    )

    to_wallet = WalletFactory(
        user=from_wallet.user,
        balance=Decimal("500.00"),
    )

    transfer = TransferService.create(
        validated_data={
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": Decimal("300.00"),
            "description": "Transfer",
            "transfer_date": date.today(),
        }
    )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    assert Transfer.objects.filter(id=transfer.id).exists()
    assert transfer.amount == Decimal("300.00")
    assert transfer.from_wallet == from_wallet
    assert transfer.to_wallet == to_wallet

    assert from_wallet.balance == Decimal("700.00")
    assert to_wallet.balance == Decimal("800.00")


def test_create_transfer_insufficient_funds():
    from_wallet = WalletFactory(
        balance=Decimal("100.00"),
    )

    to_wallet = WalletFactory(
        user=from_wallet.user,
        balance=Decimal("500.00"),
    )

    with pytest.raises(ValidationError):
        TransferService.create(
            validated_data={
                "from_wallet": from_wallet,
                "to_wallet": to_wallet,
                "amount": Decimal("300.00"),
                "description": "Transfer",
                "transfer_date": date.today(),
            }
        )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    assert not Transfer.objects.filter(from_wallet=from_wallet, to_wallet=to_wallet).exists()
    assert from_wallet.balance == Decimal("100.00")
    assert to_wallet.balance == Decimal("500.00")


def test_create_transfer_exact_balance():
    from_wallet = WalletFactory(
        balance=Decimal("300.00"),
    )

    to_wallet = WalletFactory(
        user=from_wallet.user,
        balance=Decimal("0.00"),
    )

    transfer = TransferService.create(
        validated_data={
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": Decimal("300.00"),
            "description": "Transfer",
            "transfer_date": date.today(),
        }
    )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()

    assert transfer.amount == Decimal("300.00")
    assert from_wallet.balance == Decimal("0.00")
    assert to_wallet.balance == Decimal("300.00")


def test_create_transfer_does_not_affect_other_wallets():
    from_wallet = WalletFactory(
        balance=Decimal("1000.00"),
    )

    to_wallet = WalletFactory(
        user=from_wallet.user,
        balance=Decimal("500.00"),
    )

    third_wallet = WalletFactory(
        user=from_wallet.user,
        balance=Decimal("999.00"),
    )

    TransferService.create(
        validated_data={
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": Decimal("200.00"),
            "description": "Transfer",
            "transfer_date": date.today(),
        }
    )

    from_wallet.refresh_from_db()
    to_wallet.refresh_from_db()
    third_wallet.refresh_from_db()

    assert from_wallet.balance == Decimal("800.00")
    assert to_wallet.balance == Decimal("700.00")
    assert third_wallet.balance == Decimal("999.00")


def test_create_transfer_same_wallet():
    wallet = WalletFactory(
        balance=Decimal("1000.00"),
    )

    with pytest.raises(ValidationError):
        TransferService.create(
            validated_data={
                "from_wallet": wallet,
                "to_wallet": wallet,
                "amount": Decimal("300.00"),
                "description": "Transfer",
                "transfer_date": date.today(),
            }
        )

    wallet.refresh_from_db()

    assert not Transfer.objects.filter(from_wallet=wallet, to_wallet=wallet).exists()
    assert wallet.balance == Decimal("1000.00")