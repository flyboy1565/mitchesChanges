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
        verbose_name_plural = "Stream Users"


class ChatRoom(models.Model):
    room_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=60, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'rooms'
        verbose_name_plural = "Chat Rooms"


class ChatMessages(models.Model):
    twith_id = models.CharField(max_length=50, unique=True, primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='messages', on_delete=models.DO_NOTHING)
    room = models.ForeignKey(ChatRoom, related_name='room', on_delete=models.DO_NOTHING)
    message = models.TextField()

    def __str__(self) -> str:
        return f"{self.room} - {self.user__username}"

    class Meta: 
        db_table = "chat_messages"
        verbose_name_plural = "Chat Messages"
    

class CommandUse(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='command_usage', on_delete=models.DO_NOTHING)
    message = models.ForeignKey(ChatMessages, related_name="cu_message", on_delete=models.DO_NOTHING)
    command = models.CharField(max_length=60)
    is_custom = models.BooleanField()

    class Meta: 
        db_table = "command_use"
        

class TextCommands(models.Model):
    command = models.CharField(max_length=60)
    message = models.TextField()

    def __str__(self) -> str:
        return self.command

    class Meta: 
        db_table = "text_commands"
        verbose_name_plural = "Text Commands"


class FalseCommands(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='false_commands', on_delete=models.DO_NOTHING)
    message = models.ForeignKey(ChatMessages, related_name="fc_message", on_delete=models.DO_NOTHING)
    command = models.CharField(max_length=60)

    class Meta: 
        db_table = "false_commands"
        verbose_name_plural = "False Commands"


class BotTime(models.Model):
    uptime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.uptime.strftime('%Y-%m-%d %H:%M:%S')

    class Meta: 
        db_table = "bot_time"


class FeatureRequest(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(StreamUsers, related_name='feature_requests', on_delete=models.DO_NOTHING)
    msg_link = models.ForeignKey(ChatMessages, related_name="fr_message", on_delete=models.DO_NOTHING)
    message = models.TextField()
    added_to_tasks = models.BooleanField()

    class Meta: 
        db_table = "feature_requests"


class RoomsToMonitor(models.Model):
    name = models.CharField(max_length=60, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    last_monitored = models.DateTimeField(auto_now=True)
    active = models.BooleanField()

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'rooms_to_monitor'
        verbose_name_plural = "Rooms to Monitor"