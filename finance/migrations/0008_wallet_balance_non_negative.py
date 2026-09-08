from decimal import Decimal

from django.db import migrations, models


def ensure_non_negative_wallet_balances(apps, schema_editor):
    wallet_model = apps.get_model("finance", "Wallet")
    negative_wallet_ids = list(
        wallet_model.objects.filter(balance__lt=Decimal("0.00")).values_list(
            "id",
            flat=True,
        )[:10]
    )

    if negative_wallet_ids:
        ids = ", ".join(str(wallet_id) for wallet_id in negative_wallet_ids)
        raise RuntimeError(
            "Cannot add the non-negative wallet balance constraint. "
            f"Wallets with negative balances exist (IDs: {ids})."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0007_protect_financial_history"),
    ]

    operations = [
        migrations.RunPython(
            ensure_non_negative_wallet_balances,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="wallet",
            constraint=models.CheckConstraint(
                condition=models.Q(("balance__gte", Decimal("0.00"))),
                name="wallet_balance_non_negative",
            ),
        ),
    ]
