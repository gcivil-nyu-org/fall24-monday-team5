# Generated by Django 5.1.2 on 2024-11-21 05:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("messaging", "0002_contact_is_friend"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contact",
            name="added_on",
        ),
        migrations.AlterField(
            model_name="message",
            name="timestamp",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
