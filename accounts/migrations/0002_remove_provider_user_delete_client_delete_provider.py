# Generated by Django 5.1.2 on 2024-11-06 21:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="provider",
            name="user",
        ),
        migrations.DeleteModel(
            name="Client",
        ),
        migrations.DeleteModel(
            name="Provider",
        ),
    ]
