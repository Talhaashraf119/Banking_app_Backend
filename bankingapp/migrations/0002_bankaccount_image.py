# Generated by Django 5.1.1 on 2025-03-16 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankingapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='image',
            field=models.ImageField(default=None, upload_to='uploads/images/'),
        ),
    ]
