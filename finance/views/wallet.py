from django.db.models.deletion import ProtectedError
from rest_framework import viewsets

from finance.exceptions import ResourceConflict
from finance.models.wallet import Wallet
from finance.serializers.wallet import WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer

    def get_queryset(
        self,
    ):

        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        is_in_use = (
            instance.transactions.exists()
            or instance.outgoing_transfers.exists()
            or instance.incoming_transfers.exists()
        )

        if is_in_use:
            raise ResourceConflict(
                "Wallet cannot be deleted because it has transactions or transfers."
            )

        try:
            instance.delete()
        except ProtectedError as error:
            raise ResourceConflict(
                "Wallet cannot be deleted because it is in use."
            ) from error
