import factory

from finance.models import Category
from finance.models.choices import CategoryType

from .user_factory import UserFactory


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    type = CategoryType.EXPENSE
