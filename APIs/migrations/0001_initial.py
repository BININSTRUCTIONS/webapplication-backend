# Generated by Django 4.2.14 on 2025-03-02 10:20

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="APIInfo",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("calls_per_minutes", models.IntegerField(default=12)),
            ],
        ),
    ]
