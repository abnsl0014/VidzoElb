# Generated by Django 4.1.1 on 2023-12-26 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0020_rename_phonenumber_reminder_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='status',
            field=models.CharField(choices=[('1', 'NOT_STARTED'), ('2', 'IN_PROCESS'), ('3', 'DISCARDED'), ('4', 'DONE')], default='1', max_length=4),
        ),
    ]