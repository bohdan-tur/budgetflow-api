from decimal import Decimal
from typing import Any

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

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
            Wallet.objects.filter(id=wallet_id).update(balance=F("balance") + delta)

    @staticmethod
    @transaction.atomic
    def create(*, validated_data: dict[str, Any]) -> Transaction:
        category: Category = validated_data["category"]
        amount: Decimal = validated_data["amount"]
        wallet_data: Wallet = validated_data["wallet"]

        wallet = Wallet.objects.select_for_update().get(id=wallet_data.id)

        if category.type == CategoryType.EXPENSE and wallet.balance < amount:
            raise ValidationError("Insufficient funds in the wallet.")

        transaction_obj = Transaction.objects.create(**validated_data)
        delta = TransactionService._get_delta(category, amount)

        wallet.balance += delta
        wallet.save(update_fields=["balance"])

        return transaction_obj

    @staticmethod
    @transaction.atomic
    def update(
        *,
        instance: Transaction,
        validated_data: dict[str, Any],
    ) -> Transaction:
        old_wallet = Wallet.objects.select_for_update().get(id=instance.wallet_id)

        old_delta = TransactionService._get_delta(
            instance.category,
            instance.amount,
        )
        old_wallet_id = instance.wallet_id

        new_wallet_id = validated_data.get("wallet", instance.wallet).id
        new_category = validated_data.get("category", instance.category)
        new_amount = validated_data.get("amount", instance.amount)
        new_delta = TransactionService._get_delta(new_category, new_amount)

        if old_wallet_id == new_wallet_id:
            net_delta = new_delta - old_delta
            if old_wallet.balance + net_delta < Decimal("0.00"):
                raise ValidationError("Insufficient funds in the wallet after update.")
        else:
            new_wallet = Wallet.objects.select_for_update().get(id=new_wallet_id)
            if old_wallet.balance - old_delta < Decimal("0.00"):
                raise ValidationError(
                    "Insufficient funds in the old wallet to revert transaction."
                )
            if new_wallet.balance + new_delta < Decimal("0.00"):
                raise ValidationError("Insufficient funds in the target wallet.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if validated_data:
            instance.save(update_fields=list(validated_data.keys()))

        if old_wallet_id == instance.wallet_id:
            net_delta = new_delta - old_delta
            old_wallet.balance += net_delta
            old_wallet.save(update_fields=["balance"])
        else:
            new_wallet = Wallet.objects.select_for_update().get(id=instance.wallet_id)
            old_wallet.balance -= old_delta
            old_wallet.save(update_fields=["balance"])
            new_wallet.balance += new_delta
            new_wallet.save(update_fields=["balance"])

        return instance

    @staticmethod
    @transaction.atomic
    def destroy(*, instance: Transaction) -> None:
        wallet = Wallet.objects.select_for_update().get(id=instance.wallet_id)

        delta = TransactionService._get_delta(
            instance.category,
            instance.amount,
        )

        if wallet.balance - delta < Decimal("0.00"):
            raise ValidationError("Insufficient funds to delete this transaction.")

        wallet.balance -= delta
        wallet.save(update_fields=["balance"])
        instance.delete()
