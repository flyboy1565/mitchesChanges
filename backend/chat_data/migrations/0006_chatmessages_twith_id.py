# Generated by Django 3.2.3 on 2021-05-25 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_data', '0005_auto_20210524_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='twith_id',
            field=models.CharField(default='', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]
