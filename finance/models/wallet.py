from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .choices import Currency


class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets",
    )

    name = models.CharField(max_length=100)

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.UAH,
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_wallet_name_per_user",
            )
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.currency})"
