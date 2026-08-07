from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce

from finance.models.budget import Budget
from finance.models.choices import CategoryType
from finance.models.transaction import Transaction

User = get_user_model()


class BudgetService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: User,
        validated_data: dict[str, Any],
    ) -> Budget:
        return Budget.objects.create(
            user=user,
            **validated_data,
        )

    @staticmethod
    @transaction.atomic
    def update(
        *,
        instance: Budget,
        validated_data: dict[str, Any],
    ) -> Budget:

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if validated_data:
            instance.save(update_fields=list(validated_data.keys()))

        return instance

    @staticmethod
    @transaction.atomic
    def destroy(
        *,
        instance: Budget,
    ) -> None:
        instance.delete()

    @staticmethod
    def get_spent_amount(*, budget: Budget) -> Decimal:
        result = Transaction.objects.filter(
            wallet__user=budget.user,
            category=budget.category,
            transaction_date__range=(
                budget.start_date,
                budget.end_date,
            ),
            category__type=CategoryType.EXPENSE,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00"),
                output_field=DecimalField(),
            )
        )

        return result["total"]

    @staticmethod
    def get_remaining_amount(*, budget: Budget) -> Decimal:
        spent = BudgetService.get_spent_amount(
            budget=budget,
        )

        return budget.amount - spent

    @staticmethod
    def get_percentage_used(*, budget: Budget) -> Decimal:
        if budget.amount == Decimal("0.00"):
            return Decimal("0.00")

        spent = BudgetService.get_spent_amount(
            budget=budget,
        )

        return ((spent / budget.amount) * Decimal("100")).quantize(Decimal("0.01"))

    @staticmethod
    def is_budget_exceeded(*, budget: Budget) -> bool:
        spent = BudgetService.get_spent_amount(
            budget=budget,
        )

        return spent > budget.amount
