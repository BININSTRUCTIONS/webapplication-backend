# Generated by Django 4.2.14 on 2025-03-07 13:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("APIs", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="apiinfo",
            old_name="calls_per_minutes",
            new_name="calls_per_minute",
        ),
    ]
