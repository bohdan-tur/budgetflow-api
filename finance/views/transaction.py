from rest_framework.viewsets import ModelViewSet
from finance.models.transaction import Transaction
from finance.serializers.transaction import TransactionSerializer
from finance.services.transaction_service import TransactionService


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return (
            Transaction.objects
            .filter(wallet__user=self.request.user)
            .select_related("wallet", "category")
        )

    def perform_create(self, serializer):
        serializer.instance = TransactionService.create(
            validated_data=serializer.validated_data
        )

    def perform_update(self, serializer):
        serializer.instance = TransactionService.update(
            instance=serializer.instance,
            validated_data=serializer.validated_data
        )

    def perform_destroy(self, instance):
        TransactionService.destroy(instance=instance)