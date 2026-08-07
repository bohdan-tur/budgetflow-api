from rest_framework import serializers

from finance.models.transfer import Transfer


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer

        fields = [
            "id",
            "from_wallet",
            "to_wallet",
            "amount",
            "description",
            "transfer_date",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_from_wallet(self, wallet):
        if wallet.user != self.context["request"].user:
            raise serializers.ValidationError("You don't have access to this wallet.")
        return wallet

    def validate_to_wallet(self, wallet):
        if wallet.user != self.context["request"].user:
            raise serializers.ValidationError("You don't have access to this wallet.")
        return wallet

    def validate(self, attrs):
        from_wallet = attrs["from_wallet"]
        to_wallet = attrs["to_wallet"]
        amount = attrs["amount"]

        if from_wallet == to_wallet:
            raise serializers.ValidationError(
                "Source and destination wallets must be different."
            )

        if from_wallet.currency != to_wallet.currency:
            raise serializers.ValidationError(
                "Transfers between wallets with different currencies are not allowed."
            )

        if from_wallet.balance < amount:
            raise serializers.ValidationError("Insufficient funds.")

        return attrs
