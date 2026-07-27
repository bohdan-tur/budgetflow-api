from decimal import Decimal
from datetime import date, timedelta

import factory

from finance.models import Budget

from .category_factory import CategoryFactory
from .user_factory import UserFactory


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)

    amount = Decimal("1000.00")

    start_date = date.today()
    end_date = date.today() + timedelta(days=30)
