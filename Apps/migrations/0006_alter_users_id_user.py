# Generated by Django 4.2.1 on 2024-03-22 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Apps', '0005_alter_users_id_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='id_user',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]