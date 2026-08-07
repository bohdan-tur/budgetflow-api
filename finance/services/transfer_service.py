from typing import Any

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from finance.models.transfer import Transfer
from finance.models.wallet import Wallet


class TransferService:
    @staticmethod
    @transaction.atomic
    def create(*, validated_data: dict[str, Any]) -> Transfer:

        unlocked_from_wallet = validated_data["from_wallet"]
        unlocked_to_wallet = validated_data["to_wallet"]
        amount = validated_data["amount"]

        wallet_ids = sorted(
            [
                unlocked_from_wallet.id,
                unlocked_to_wallet.id,
            ]
        )

        wallets = {
            wallet.id: wallet
            for wallet in Wallet.objects.select_for_update().filter(id__in=wallet_ids)
        }

        from_wallet = wallets[unlocked_from_wallet.id]
        to_wallet = wallets[unlocked_to_wallet.id]

        if from_wallet.id == to_wallet.id:
            raise ValidationError("Cannot transfer to the same wallet.")

        if from_wallet.user != to_wallet.user:
            raise ValidationError("Cannot transfer to another user's wallet.")

        if from_wallet.currency != to_wallet.currency:
            raise ValidationError(
                "Transfers between wallets with different currencies are not allowed."
            )

        if from_wallet.balance < amount:
            raise ValidationError("Insufficient funds.")

        transfer = Transfer.objects.create(**validated_data)

        Wallet.objects.filter(id=from_wallet.id).update(balance=F("balance") - amount)

        Wallet.objects.filter(id=to_wallet.id).update(balance=F("balance") + amount)

        return transfer
