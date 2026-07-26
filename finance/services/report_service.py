from decimal import Decimal

from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce

from finance.models import Wallet
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
            "total_income": ReportService.get_total_income(
                user=user,
            ),
            "total_expense": ReportService.get_total_expense(
                user=user,
            ),
            "current_balance": ReportService.get_current_balance(
                user=user,
            ),
        }