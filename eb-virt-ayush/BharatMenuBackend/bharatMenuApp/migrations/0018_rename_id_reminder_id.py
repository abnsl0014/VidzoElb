# Generated by Django 4.1.1 on 2023-12-21 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0017_rename_phone_number_reminder_phonenumber'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reminder',
            old_name='Id',
            new_name='id',
        ),
    ]
