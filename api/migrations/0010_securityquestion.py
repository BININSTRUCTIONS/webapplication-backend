# Generated by Django 4.2.14 on 2025-03-29 03:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_newslettersubscription_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SecurityQuestion",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("question", models.CharField(max_length=50)),
                ("answer", models.CharField(max_length=20)),
            ],
        ),
    ]
