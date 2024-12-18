# Generated by Django 5.1 on 2024-11-15 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mma", "0021_product_phone_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuizQuestion",
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
                ("question_text", models.TextField()),
                ("option_a", models.CharField(max_length=255)),
                ("option_b", models.CharField(max_length=255)),
                ("option_c", models.CharField(max_length=255)),
                ("option_d", models.CharField(max_length=255)),
                (
                    "correct_answer",
                    models.CharField(
                        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
                        max_length=1,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuizScore",
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
                ("phone_number", models.CharField(max_length=15)),
                ("score", models.IntegerField(default=0)),
                ("date_submitted", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("groceries", "Groceries"),
                    ("service", "Service"),
                    ("job", "Job"),
                    ("hardware", "Hardware"),
                    ("electronics", "Electronics"),
                    ("clothing", "Clothing"),
                    ("furniture", "Furniture"),
                    ("automotive", "Automotive"),
                    ("beauty_health", "Beauty & Health"),
                    ("toys", "Toys"),
                    ("sports", "Sports & Outdoors"),
                    ("books", "Books"),
                    ("home_appliances", "Home Appliances"),
                    ("stationery", "Stationery"),
                    ("pharmacy", "Pharmacy"),
                    ("jewelry", "Jewelry & Accessories"),
                    ("footwear", "Footwear"),
                    ("gardening", "Gardening & Outdoor"),
                    ("baby_products", "Baby Products"),
                    ("pet_supplies", "Pet Supplies"),
                    ("music_instruments", "Musical Instruments"),
                    ("office_supplies", "Office Supplies"),
                    ("gaming", "Gaming"),
                    ("kitchenware", "Kitchenware"),
                    ("building_materials", "Building Materials"),
                    ("tools", "Tools & Equipment"),
                    ("computer_accessories", "Computer & Accessories"),
                ],
                default="other",
                max_length=100,
            ),
        ),
    ]
