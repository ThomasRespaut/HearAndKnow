# Generated by Django 5.0.3 on 2024-03-18 12:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Apps', '0004_meeting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
