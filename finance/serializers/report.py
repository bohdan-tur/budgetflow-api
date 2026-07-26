from rest_framework import serializers


class ReportSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    current_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )