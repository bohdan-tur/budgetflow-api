from decimal import Decimal
from datetime import date

import factory

from finance.models import Transfer

from .wallet_factory import WalletFactory


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    from_wallet = factory.SubFactory(WalletFactory)
    to_wallet = factory.SubFactory(WalletFactory)

    amount = Decimal("100.00")
    transfer_date = date.today()
