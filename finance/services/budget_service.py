from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from finance.models.budget import Budget

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
            instance.save(
                update_fields=list(validated_data.keys())
            )

        return instance

    @staticmethod
    @transaction.atomic
    def destroy(
        *,
        instance: Budget,
    ) -> None:
        instance.delete()