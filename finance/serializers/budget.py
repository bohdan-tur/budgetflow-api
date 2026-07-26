from rest_framework import serializers

from finance.models.budget import Budget


class BudgetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "amount",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        if attrs["start_date"] >= attrs["end_date"]:
            raise serializers.ValidationError(
                "End date must be greater than start date."
            )

        return attrs