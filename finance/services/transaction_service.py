
from decimal import Decimal
from typing import Any
from django.db import transaction
from django.db.models import F

from finance.models.category import Category
from finance.models.choices import CategoryType
from finance.models.transaction import Transaction
from finance.models.wallet import Wallet


class TransactionService:

    @staticmethod
    def _get_delta(category: Category, amount: Decimal) -> Decimal:
        if category.type == CategoryType.INCOME:
            return amount
        elif category.type == CategoryType.EXPENSE:
            return -amount

        raise ValueError(f"Unknown category type: {category.type}")

    @staticmethod
    def _update_wallet_balance(*, wallet_id: int, delta: Decimal) -> None:
        if delta != Decimal("0.00"):
            Wallet.objects.filter(id=wallet_id).update(
                balance=F("balance") + delta
            )

    @staticmethod
    @transaction.atomic
    def create(*, validated_data: dict[str, Any]) -> Transaction:
        category: Category = validated_data["category"]
        amount: Decimal = validated_data["amount"]

        transaction_obj = Transaction.objects.create(**validated_data)

        delta = TransactionService._get_delta(category, amount)

        TransactionService._update_wallet_balance(
            wallet_id=transaction_obj.wallet_id,
            delta=delta,
        )

        return transaction_obj

    @staticmethod
    @transaction.atomic
    def update(
        *,
        instance: Transaction,
        validated_data: dict[str, Any],
    ) -> Transaction:

        old_delta = TransactionService._get_delta(
            instance.category,
            instance.amount,
        )

        old_wallet_id = instance.wallet_id

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if validated_data:
            instance.save(
                update_fields=list(validated_data.keys())
            )

        new_delta = TransactionService._get_delta(
            instance.category,
            instance.amount,
        )

        if old_wallet_id == instance.wallet_id:

            net_delta = new_delta - old_delta

            TransactionService._update_wallet_balance(
                wallet_id=old_wallet_id,
                delta=net_delta,
            )

        else:

            TransactionService._update_wallet_balance(
                wallet_id=old_wallet_id,
                delta=-old_delta,
            )

            TransactionService._update_wallet_balance(
                wallet_id=instance.wallet_id,
                delta=new_delta,
            )

        return instance

    @staticmethod
    @transaction.atomic
    def destroy(*, instance: Transaction) -> None:

        delta = TransactionService._get_delta(
            instance.category,
            instance.amount,
        )

        TransactionService._update_wallet_balance(
            wallet_id=instance.wallet_id,
            delta=-delta,
        )

        instance.delete()

