from rest_framework.viewsets import ModelViewSet

from finance.models.budget import Budget
from finance.serializers.budget import BudgetSerializer
from finance.services.budget_service import BudgetService


class BudgetViewSet(ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return (
            Budget.objects
            .filter(user=self.request.user)
            .select_related("category")
        )

    def perform_create(self, serializer):
        serializer.instance = BudgetService.create(
            user=self.request.user,
            validated_data=serializer.validated_data,
        )

    def perform_update(self, serializer):
        serializer.instance = BudgetService.update(
            instance=serializer.instance,
            validated_data=serializer.validated_data,
        )

    def perform_destroy(self, instance):
        BudgetService.destroy(
            instance=instance,
        )