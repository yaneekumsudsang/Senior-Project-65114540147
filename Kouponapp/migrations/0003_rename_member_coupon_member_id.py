# Generated by Django 5.1 on 2024-12-13 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Kouponapp", "0002_alter_coupon_options_alter_member_options_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="coupon",
            old_name="member",
            new_name="member_id",
        ),
    ]
