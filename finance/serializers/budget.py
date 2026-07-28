from rest_framework import serializers

from finance.models.budget import Budget
from finance.services.budget_service import BudgetService


class BudgetSerializer(serializers.ModelSerializer):
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()
    is_budget_exceeded = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "amount",
            "start_date",
            "end_date",
            "spent_amount",
            "remaining_amount",
            "percentage_used",
            "is_budget_exceeded",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "spent_amount",
            "remaining_amount",
            "percentage_used",
            "is_budget_exceeded",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None,
        )

        end_date = attrs.get(
            "end_date",
            self.instance.end_date if self.instance else None,
        )

        if start_date >= end_date:
            raise serializers.ValidationError(
                "End date must be greater than start date."
            )

        return attrs

    def validate_category(self, category):
        if category.user != self.context["request"].user:
            raise serializers.ValidationError(
                "You don't have access to this category."
            )
        return category

    def get_spent_amount(self, obj):
        return BudgetService.get_spent_amount(
            budget=obj,
        )

    def get_remaining_amount(self, obj):
        return BudgetService.get_remaining_amount(
            budget=obj,
        )

    def get_percentage_used(self, obj):
        return BudgetService.get_percentage_used(
            budget=obj,
        )

    def get_is_budget_exceeded(self, obj):
        return BudgetService.is_budget_exceeded(
            budget=obj,
        )