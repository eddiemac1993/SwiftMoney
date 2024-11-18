# Generated by Django 5.1 on 2024-11-01 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mma", "0020_product_store_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="phone_number",
            field=models.CharField(
                default="000-000-0000",
                help_text="Enter the store owner's contact number",
                max_length=15,
            ),
        ),
    ]