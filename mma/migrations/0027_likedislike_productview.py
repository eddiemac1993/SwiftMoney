# Generated by Django 5.1 on 2024-11-25 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mma", "0026_birthdaywish"),
    ]

    operations = [
        migrations.CreateModel(
            name="LikeDislike",
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
                    "session_key",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "action",
                    models.SmallIntegerField(choices=[(1, "Like"), (-1, "Dislike")]),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes_dislikes",
                        to="mma.product",
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "session_key", "action")},
            },
        ),
        migrations.CreateModel(
            name="ProductView",
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
                    "session_key",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("viewed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="views",
                        to="mma.product",
                    ),
                ),
            ],
            options={
                "unique_together": {("product", "session_key", "ip_address")},
            },
        ),
    ]