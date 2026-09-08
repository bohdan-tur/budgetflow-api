from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from finance.models import Wallet
from tests.factories import WalletFactory


@pytest.mark.django_db
def test_database_rejects_negative_wallet_balance():
    wallet = WalletFactory(balance=Decimal("0.00"))

    with pytest.raises(IntegrityError), transaction.atomic():
        Wallet.objects.filter(id=wallet.id).update(balance=Decimal("-0.01"))

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("0.00")
