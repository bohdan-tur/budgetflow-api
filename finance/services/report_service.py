from decimal import Decimal
from django.db.models import DecimalField, F, Sum, Q
from django.db.models.functions import Coalesce, TruncMonth
from finance.models import Wallet, Category
from finance.models.choices import CategoryType
from finance.models.transaction import Transaction


class ReportService:

    @staticmethod
    def get_total_income(*, user) -> Decimal:
        result = (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.INCOME,
            )
            .aggregate(
                total=Coalesce(
                    Sum("amount"),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                )
            )
        )
        return result["total"]

    @staticmethod
    def get_total_expense(*, user) -> Decimal:
        result = (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.EXPENSE,
            )
            .aggregate(
                total=Coalesce(
                    Sum("amount"),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                )
            )
        )
        return result["total"]

    @staticmethod
    def get_current_balance(*, user) -> Decimal:
        result = (
            Wallet.objects.filter(
                user=user,
            ).aggregate(
                total=Coalesce(
                    Sum("balance"),
                    Decimal("0.00"),
                    output_field=DecimalField(),
                )
            )
        )
        return result["total"]

    @staticmethod
    def get_summary(*, user) -> dict[str, Decimal]:
        return {
            "total_income": ReportService.get_total_income(user=user),
            "total_expense": ReportService.get_total_expense(user=user),
            "current_balance": ReportService.get_current_balance(user=user),
        }

    @staticmethod
    def get_expenses_by_category(*, user):
        return (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.EXPENSE,
            )
            .values(category=F("category__name"))
            .annotate(total=Sum("amount"))
        )

    @staticmethod
    def get_income_by_category(*, user):
        return (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.INCOME,
            )
            .values(category=F("category__name"))
            .annotate(total=Sum("amount"))
        )

    @staticmethod
    def get_monthly_statistics(*, user):
        return (
            Transaction.objects.filter(wallet__user=user)
            .annotate(month=TruncMonth("transaction_date"))
            .values("month")
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
            .order_by("month")
        )

    @staticmethod
    def get_statistics_by_period(*, user, start_time=None, end_time=None):
        queryset = Transaction.objects.filter(wallet__user=user)

        if start_time:
            queryset = queryset.filter(transaction_date__gte=start_time)

        if end_time:
            queryset = queryset.filter(transaction_date__lte=end_time)

        return queryset.aggregate(
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

    @staticmethod
    def get_top_expense_categories(*, user, limit=5):
        return (
            Transaction.objects.filter(
                wallet__user=user,
                category__type=CategoryType.EXPENSE,
            )
            .values(category=F("category__name"))
            .annotate(total=Sum("amount"))
            .order_by("-total")[:limit]
        )
