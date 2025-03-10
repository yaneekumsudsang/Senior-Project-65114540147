# Generated by Django 5.1 on 2025-02-11 08:54

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Kouponapp", "0004_wallet_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wallet",
            name="balance",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                verbose_name="ยอดเงินคงเหลือ",
            ),
        ),
    ]
