# Generated by Django 4.1.1 on 2023-03-31 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0008_merchant_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='otpVerified',
            field=models.BooleanField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='fullName',
            field=models.CharField(default='', max_length=100),
        ),
    ]
