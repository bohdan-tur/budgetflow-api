from decimal import Decimal

import factory

from finance.models import Wallet
from finance.models.choices import Currency

from .user_factory import UserFactory


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Wallet

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Wallet {n}")
    currency = Currency.UAH
    balance = Decimal("1000.00")
