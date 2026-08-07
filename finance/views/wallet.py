from rest_framework import viewsets

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
