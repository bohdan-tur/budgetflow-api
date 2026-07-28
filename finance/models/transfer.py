from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from .wallet import Wallet


class Transfer(models.Model):
    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="outgoing_transfers",
    )

    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name="incoming_transfers",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    description = models.TextField(
        blank=True,
    )

    transfer_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-transfer_date", "-created_at"]
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"

    def __str__(self):
        return f"{self.from_wallet.name} → {self.to_wallet.name}: {self.amount}"
