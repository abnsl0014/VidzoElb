# Generated by Django 4.1.1 on 2023-05-10 13:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0009_profile_otpverified_alter_profile_fullname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('QueryId', models.AutoField(primary_key=True, serialize=False)),
                ('queryType', models.CharField(choices=[('1', 'TEXT'), ('2', 'VIDEO')], default='1', max_length=2)),
                ('query', models.CharField(default='', max_length=5000)),
                ('businessName', models.CharField(default='', max_length=500)),
                ('queryDateTime', models.DateTimeField(auto_now_add=True)),
                ('VideoAd', models.FileField(null=True, upload_to='videos_uploaded', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])),
                ('TextAd', models.CharField(default='', max_length=5000)),
                ('status', models.CharField(choices=[('1', 'NOT_STARTED'), ('2', 'IN_PROCESS'), ('3', 'DISCARDED'), ('4', 'DONE')], default='1', max_length=4)),
                ('profileId', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='bharatMenuApp.profile')),
            ],
        ),
    ]
