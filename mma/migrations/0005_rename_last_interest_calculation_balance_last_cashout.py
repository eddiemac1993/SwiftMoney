# Generated by Django 5.1 on 2024-08-21 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mma", "0004_rename_last_cashout_balance_last_interest_calculation"),
    ]

    operations = [
        migrations.RenameField(
            model_name="balance",
            old_name="last_interest_calculation",
            new_name="last_cashout",
        ),
    ]