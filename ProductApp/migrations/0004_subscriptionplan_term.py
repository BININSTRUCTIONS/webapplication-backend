# Generated by Django 4.2.14 on 2025-02-22 11:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ProductApp", "0003_subscriptionplanitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscriptionplan",
            name="term",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
