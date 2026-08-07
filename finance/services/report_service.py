from decimal import Decimal

from django.db.models import DecimalField, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth

from finance.models import Wallet
from finance.models.choices import CategoryType
from finance.models.transaction import Transaction


class ReportService:
    @staticmethod
    def get_summary(*, user) -> dict[str, list[dict]]:
        balances = {
            item["currency"]: item["current_balance"]
            for item in Wallet.objects.filter(user=user)
            .values("currency")
            .annotate(
                current_balance=Coalesce(
                    Sum("balance"),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                )
            )
        }

        transaction_totals = {
            item["currency"]: item
            for item in Transaction.objects.filter(wallet__user=user)
            .annotate(currency=F("wallet__currency"))
            .values("currency")
            .annotate(
                total_income=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.INCOME)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
                total_expense=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.EXPENSE)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
            )
        }

        currencies = []
        for currency, current_balance in sorted(balances.items()):
            totals = transaction_totals.get(currency, {})
            currencies.append(
                {
                    "currency": currency,
                    "total_income": totals.get("total_income", Decimal("0.00")),
                    "total_expense": totals.get("total_expense", Decimal("0.00")),
                    "current_balance": current_balance,
                }
            )

        return {"currencies": currencies}

    @staticmethod
    def get_expenses_by_category(*, user):
        return (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.EXPENSE,
            )
            .annotate(
                category_name=F("category__name"),
                currency=F("wallet__currency"),
            )
            .values("currency", "category_name")
            .annotate(total=Sum("amount"))
            .order_by("currency", "category_name")
        )

    @staticmethod
    def get_income_by_category(*, user):
        return (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.INCOME,
            )
            .annotate(
                category_name=F("category__name"),
                currency=F("wallet__currency"),
            )
            .values("currency", "category_name")
            .annotate(total=Sum("amount"))
            .order_by("currency", "category_name")
        )

    @staticmethod
    def get_monthly_statistics(*, user):
        return (
            Transaction.objects.filter(wallet__user=user)
            .annotate(
                month=TruncMonth("transaction_date"),
                currency=F("wallet__currency"),
            )
            .values("month", "currency")
            .annotate(
                income=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.INCOME)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
                expense=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.EXPENSE)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
            )
            .order_by("month", "currency")
        )

    @staticmethod
    def get_statistics_by_period(*, user, start_time=None, end_time=None):
        queryset = Transaction.objects.filter(wallet__user=user)

        if start_time:
            queryset = queryset.filter(transaction_date__gte=start_time)

        if end_time:
            queryset = queryset.filter(transaction_date__lte=end_time)

        currencies = list(
            queryset.annotate(currency=F("wallet__currency"))
            .values("currency")
            .annotate(
                total_income=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.INCOME)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
                total_expense=Coalesce(
                    Sum("amount", filter=Q(category__type=CategoryType.EXPENSE)),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                ),
            )
            .order_by("currency")
        )

        return {"currencies": currencies}

    @staticmethod
    def get_top_expense_categories(*, user, limit=5):
        rows = (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.EXPENSE,
            )
            .annotate(
                category_name=F("category__name"),
                currency=F("wallet__currency"),
            )
            .values("currency", "category_name")
            .annotate(total=Sum("amount"))
            .order_by("currency", "-total", "category_name")
        )

        result = []
        currency_counts = {}

        for row in rows:
            currency = row["currency"]
            currency_counts.setdefault(currency, 0)

            if currency_counts[currency] < limit:
                result.append(row)
                currency_counts[currency] += 1

        return result
