import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0006_budget"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="wallet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="finance.wallet",
            ),
        ),
        migrations.AlterField(
            model_name="budget",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="budgets",
                to="finance.category",
            ),
        ),
    ]
