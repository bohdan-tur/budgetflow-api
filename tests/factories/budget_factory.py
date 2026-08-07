from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone

from finance.models import Budget
from finance.models.choices import CategoryType

from .category_factory import CategoryFactory
from .user_factory import UserFactory


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)

    category = factory.SubFactory(
        CategoryFactory,
        user=factory.SelfAttribute("..user"),
        type=CategoryType.EXPENSE,
    )

    amount = Decimal("1000.00")

    start_date = factory.LazyFunction(
        timezone.localdate,
    )

    end_date = factory.LazyFunction(
        lambda: timezone.localdate() + timedelta(days=30),
    )
