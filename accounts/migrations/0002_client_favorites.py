# Generated by Django 5.1.2 on 2024-11-06 22:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="favorites",
            field=models.ManyToManyField(
                blank=True, related_name="favorited_by", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
