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


class PeriodStatisticSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class CategoryReportSerializer(serializers.Serializer):
    category_name = serializers.CharField()

    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class MonthlyStatisticSerializer(serializers.Serializer):
    month = serializers.DateField()

    income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )