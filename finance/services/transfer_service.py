from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

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
            for wallet in Wallet.objects.select_for_update().filter(
                id__in=wallet_ids
            )
        }

        from_wallet = wallets[unlocked_from_wallet.id]
        to_wallet = wallets[unlocked_to_wallet.id]

        if from_wallet.balance < amount:
            raise ValidationError(
                "Insufficient funds."
            )

        transfer = Transfer.objects.create(
            **validated_data
        )

        Wallet.objects.filter(
            id=from_wallet.id
        ).update(
            balance=F("balance") - amount
        )

        Wallet.objects.filter(
            id=to_wallet.id
        ).update(
            balance=F("balance") + amount
        )

        return transfer