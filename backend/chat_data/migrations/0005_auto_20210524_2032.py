# Generated by Django 3.2.3 on 2021-05-24 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat_data', '0004_chatmessages_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.PositiveIntegerField(unique=True)),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
            options={
                'db_table': 'rooms',
            },
        ),
        migrations.AlterField(
            model_name='chatmessages',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='room', to='chat_data.chatroom'),
        ),
    ]
