from decimal import Decimal

import factory

from finance.models import Transaction

from .category_factory import CategoryFactory
from .wallet_factory import WalletFactory


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    wallet = factory.SubFactory(WalletFactory)
    category = factory.SubFactory(CategoryFactory)

    amount = Decimal("100.00")
    description = factory.Faker("sentence")
