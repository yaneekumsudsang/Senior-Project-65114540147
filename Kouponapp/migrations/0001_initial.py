# Generated by Django 5.1 on 2024-12-12 07:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Promotion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "picture",
                    models.ImageField(blank=True, null=True, upload_to="promotions/"),
                ),
                ("cupsize", models.CharField(blank=True, max_length=50, null=True)),
                ("cups", models.IntegerField(blank=True, null=True)),
                (
                    "discount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("free", models.IntegerField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("start", models.DateField()),
                ("end", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "profile_img",
                    models.ImageField(blank=True, null=True, upload_to="profiles/"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Owner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=15, null=True)),
                (
                    "shop_logo",
                    models.ImageField(blank=True, null=True, upload_to="shop_logos/"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("used", models.BooleanField(default=False)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Kouponapp.member",
                    ),
                ),
                (
                    "promotion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Kouponapp.promotion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Store",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("store_name", models.CharField(max_length=255, unique=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stores",
                        to="Kouponapp.owner",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="promotion",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="promotions",
                to="Kouponapp.store",
            ),
        ),
    ]
