# Generated by Django 4.1.1 on 2023-11-25 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0012_query_audiofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='AudioFile',
            field=models.FileField(blank=True, null=True, upload_to='audios_uploaded/'),
        ),
    ]
