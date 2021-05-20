# Generated by Django 3.2.3 on 2021-05-19 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamusers',
            name='banned',
            field=models.BooleanField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='streamusers',
            name='banned_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
