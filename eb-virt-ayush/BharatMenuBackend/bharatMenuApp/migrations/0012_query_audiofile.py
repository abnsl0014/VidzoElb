# Generated by Django 4.1.1 on 2023-11-25 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bharatMenuApp', '0011_query_businesstype_query_businessurl_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='AudioFile',
            field=models.FileField(blank=True, null=True, upload_to='audio/'),
        ),
    ]
