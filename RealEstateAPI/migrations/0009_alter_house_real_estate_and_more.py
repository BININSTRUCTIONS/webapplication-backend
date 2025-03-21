# Generated by Django 4.2.14 on 2024-12-07 13:20

import RealEstateAPI.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("RealEstateAPI", "0008_alter_propertymedia_media_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="house",
            name="real_estate",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="RealEstateAPI.realestate",
            ),
        ),
        migrations.AlterField(
            model_name="propertymedia",
            name="media_path",
            field=models.FileField(upload_to=RealEstateAPI.models.user_directory_path),
        ),
    ]
