# Generated by Django 4.2.14 on 2025-04-30 05:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0017_apikey_renew_frequency_apikey_renew_times"),
    ]

    operations = [
        migrations.DeleteModel(
            name="APIKey",
        ),
    ]
