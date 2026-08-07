from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from finance.models.category import Category


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="budgets",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    start_date = models.DateField()

    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "category",
                    "start_date",
                    "end_date",
                ],
                name="unique_budget_per_period",
            )
        ]

    def __str__(self):
        return f"{self.user.username} | {self.category.name} | {self.amount}"
