# Generated by Django 4.2.1 on 2024-03-21 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Apps", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="meeting",
            name="key",
        ),
    ]