from rest_framework import serializers

from finance.models.choices import Currency


class PeriodQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "Start date must not be greater than end date."
            )

        return attrs


class TopCategoriesQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(
        required=False,
        default=5,
        min_value=1,
        max_value=100,
    )


class CurrencySummarySerializer(serializers.Serializer):
    currency = serializers.ChoiceField(choices=Currency.choices)

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


class ReportSerializer(serializers.Serializer):
    currencies = CurrencySummarySerializer(many=True)


class CurrencyPeriodStatisticSerializer(serializers.Serializer):
    currency = serializers.ChoiceField(choices=Currency.choices)

    total_income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total_expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class PeriodStatisticSerializer(serializers.Serializer):
    currencies = CurrencyPeriodStatisticSerializer(many=True)


class CategoryReportSerializer(serializers.Serializer):
    currency = serializers.ChoiceField(choices=Currency.choices)
    category_name = serializers.CharField()

    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class MonthlyStatisticSerializer(serializers.Serializer):
    month = serializers.DateField()
    currency = serializers.ChoiceField(choices=Currency.choices)

    income = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    expense = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
