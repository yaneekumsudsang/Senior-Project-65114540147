# Generated by Django 5.1 on 2024-10-10 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Kouponapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promotion",
            name="expiration_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
