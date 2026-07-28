from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from finance.models.transfer import Transfer
from finance.serializers.transfer import TransferSerializer
from finance.services.transfer_service import TransferService


class TransferViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = TransferSerializer

    def get_queryset(self):
        return Transfer.objects.filter(
            from_wallet__user=self.request.user
        ).select_related(
            "from_wallet",
            "to_wallet",
        )

    def perform_create(self, serializer):
        serializer.instance = TransferService.create(
            validated_data=serializer.validated_data
        )
