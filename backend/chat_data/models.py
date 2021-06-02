from django import db
from django.db import models


class StreamUsers(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True, unique=True)
    username = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True)
    last_watched = models.DateTimeField(auto_now=True)
    following = models.BooleanField()
    followed_at = models.DateTimeField(blank=True, null=True)
    banned = models.BooleanField()
    banned_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username
    

    class Meta: 
        db_table = "followers"


class ChatRoom(models.Model):
    room_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=60, unique=True)

    class Meta:
        db_table = 'rooms'


class ChatMessages(models.Model):
    twith_id = models.CharField(max_length=50, unique=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='messages', on_delete=models.DO_NOTHING)
    room = models.ForeignKey(ChatRoom, related_name='room', on_delete=models.DO_NOTHING)
    message = models.TextField()

    class Meta: 
        db_table = "chat_messages"
    

class CommandUse(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='command_usage', on_delete=models.DO_NOTHING)
    command = models.CharField(max_length=60)
    is_custom = models.BooleanField()

    class Meta: 
        db_table = "command_use"
        

class TextCommands(models.Model):
    command = models.CharField(max_length=60)
    message = models.TextField()

    class Meta: 
        db_table = "text_commands"


class FalseCommands(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='false_commands', on_delete=models.DO_NOTHING)
    command = models.CharField(max_length=60)

    class Meta: 
        db_table = "false_commands"


class BotTime(models.Model):
    uptime = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = "bot_time"


class FeatureRequest(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='feature_requests', on_delete=models.DO_NOTHING)
    message = models.TextField()
    added_to_tasks = models.BooleanField()

    class Meta: 
        db_table = "feature_requests"


class RoomsToMonitor(models.Model):
    name = models.CharField(max_length=60, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_monitored = models.DateTimeField(auto_now=True)
    active = models.BooleanField()

    class Meta:
        db_table = 'rooms_to_monitor'