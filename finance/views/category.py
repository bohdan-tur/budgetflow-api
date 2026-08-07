from django.db.models.deletion import ProtectedError
from rest_framework.viewsets import ModelViewSet

from finance.exceptions import ResourceConflict
from finance.models.category import Category
from finance.serializers.category import CategorySerializer


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):

        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.transactions.exists() or instance.budgets.exists():
            raise ResourceConflict(
                "Category cannot be deleted because it is used in transactions "
                "or budgets."
            )

        try:
            instance.delete()
        except ProtectedError as error:
            raise ResourceConflict(
                "Category cannot be deleted because it is in use."
            ) from error
