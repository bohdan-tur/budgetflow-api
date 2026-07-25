from rest_framework import serializers

from finance.models import Wallet


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = [
            "id",
            "name",
            "balance",
            "currency",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "balance",
            "created_at",
            "updated_at",
        ]