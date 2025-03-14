# Generated by Django 5.1 on 2025-02-11 07:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Kouponapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="wallet_balance",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="collect_qr_code_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="collect_qr_codes/",
                verbose_name="ภาพ QR Code สำหรัลสะสมคูปอง",
            ),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="use_qr_code_url_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="use_qr_codes/",
                verbose_name="ภาพ QR Code สำหรับใช้คูปอง",
            ),
        ),
        migrations.CreateModel(
            name="Payment",
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_code", models.CharField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "รอการชำระเงิน"),
                            ("SUCCESS", "ชำระเงินสำเร็จ"),
                            ("FAILED", "ชำระเงินไม่สำเร็จ"),
                            ("EXPIRED", "หมดอายุ"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "qr_code",
                    models.ImageField(blank=True, null=True, upload_to="payment_qrs/"),
                ),
                (
                    "coupon",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="Kouponapp.coupon",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments_made",
                        to="Kouponapp.member",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Kouponapp.store",
                    ),
                ),
            ],
        ),
    ]
