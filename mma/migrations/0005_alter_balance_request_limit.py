# Generated by Django 5.1 on 2024-09-15 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mma", "0004_product_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="balance",
            name="request_limit",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
        ),
    ]