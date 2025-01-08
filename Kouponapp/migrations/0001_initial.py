# Generated by Django 5.1 on 2025-01-07 06:31

import django.core.validators
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
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="promotions/",
                        verbose_name="รูปโปรโมชั่น",
                    ),
                ),
                (
                    "cupsize",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="ขนาดแก้ว"
                    ),
                ),
                (
                    "cups",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="จำนวนแก้วที่สะสม"
                    ),
                ),
                (
                    "discount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="ส่วนลด",
                    ),
                ),
                (
                    "free",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="จำนวนแก้วที่ฟรี"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="ชื่อโปรโมชั่น")),
                (
                    "details",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="รายละเอียดโปรโมชั่น",
                    ),
                ),
                ("start", models.DateField(verbose_name="วันที่เริ่มใช้งานคูปอง")),
                ("end", models.DateField(verbose_name="วันหมดอายุคูปอง")),
                (
                    "count",
                    models.PositiveIntegerField(default=0, verbose_name="จำนวนคูปอง"),
                ),
            ],
            options={
                "verbose_name": "โปรโมชั่น",
                "verbose_name_plural": "โปรโมชั่น",
            },
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
                (
                    "is_owner",
                    models.BooleanField(default=False, verbose_name="เป็นเจ้าของร้าน"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=10, null=True, verbose_name="เบอร์โทรศัพท์"
                    ),
                ),
                (
                    "profile_img",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="profiles/",
                        verbose_name="รูปโปรไฟล์",
                    ),
                ),
                (
                    "shop_logo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="shop_logos/",
                        verbose_name="โลโก้ร้าน",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ชื่อผู้ใช้",
                    ),
                ),
            ],
            options={
                "verbose_name": "สมาชิก",
                "verbose_name_plural": "สมาชิก",
            },
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True, serialize=False, verbose_name="ไอดีคูปอง"
                    ),
                ),
                (
                    "promotion_count",
                    models.PositiveIntegerField(
                        max_length=200, verbose_name="ลำดับคูปอง"
                    ),
                ),
                (
                    "used",
                    models.BooleanField(default=False, verbose_name="ตรวจสอบการใช้งาน"),
                ),
                (
                    "qr_code_url",
                    models.URLField(
                        blank=True, null=True, verbose_name="URL ของ QR Code"
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Kouponapp.member",
                        verbose_name="สมาชิกที่ใช้งานคูปอง",
                    ),
                ),
                (
                    "promotion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Kouponapp.promotion",
                        verbose_name="ไอดีโปรโมชั่น",
                    ),
                ),
            ],
            options={
                "verbose_name": "คูปอง",
                "verbose_name_plural": "คูปอง",
            },
        ),
        migrations.CreateModel(
            name="Store",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("store_name", models.CharField(max_length=255, verbose_name="ชื่อร้าน")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stores",
                        to="Kouponapp.member",
                        verbose_name="เจ้าของร้าน",
                    ),
                ),
            ],
            options={
                "verbose_name": "ร้านค้า",
                "verbose_name_plural": "ร้านค้าทั้งหมด",
            },
        ),
        migrations.AddField(
            model_name="promotion",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="promotions",
                to="Kouponapp.store",
                verbose_name="ชื่อร้าน",
            ),
        ),
    ]
