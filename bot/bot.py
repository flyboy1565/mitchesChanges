import os
import re
import socket
import command
import requests
import pyttsx3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("./credentials.env")

DJANGO_URL = "http://backend:8000/api"

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


class Bot():
    def __init__(self):
        self.server = "irc.twitch.tv"
        self.port = 6667
        self.oauth_token = os.getenv('OAUTH_TOKEN')
        self.bot_name = os.getenv('BOT_NAME')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.bearer = self.get_bearer()
        self.user_name = os.getenv('USERNAME')
        self.bot_trigger = os.getenv('BOT_TRIGGER')
        self.DJANGO_URL = DJANGO_URL
        self.commands = {s.command_name: s for s in (c(self) for c in command.CommandBase.__subclasses__())}
        self.text_commands = self.reload_text_commands()
        self.channel = self.get_channels_to_monitor()
        self.TwitchBaseUrl = "https://api.twitch.tv/helix/"
        self.message_trigger = 0
        self.current_monitoring = []

    @staticmethod
    def bot_say(text):
        engine.say(text)
        engine.runAndWait()

    def get_bearer(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type" : "client_credentials"
        }
        response = requests.post(url, params = params, timeout=3)
        if response.status_code >= 200 and response.status_code < 300: 
            data = response.json()
            bearer = data["access_token"]
            return bearer
        else:
            print(f'Bearer Requesst Failed: {response.status_code}')
            print(f'Request URL: {response.request.url}')
            print(f'Bearer Requesst Failed: {response.content}')


    # connect to IRC server and begin checking for messages
    def connect_to_channel(self):
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.bot_name}")
        for channel in self.channel:
            is_live = self.check_if_channel_is_live(channel)
            if is_live is not None and channel not in self.current_monitoring:
                text = f'{channel} is live and started at {is_live["started_at"]}'
                print(text)
                self.current_monitoring.append(channel)
                self.irc_command(f"JOIN #{channel}")
                self.send_message(channel, "Hello All!")
        self.irc_command(f"CAP REQ :twitch.tv/tags")        
        self.check_for_messages()


    def get_channels_to_monitor(self):
        response = requests.get(f'{self.DJANGO_URL}/monitor_rooms/')
        if response.status_code < 300:
            channels = [i['name'] for i in response.json() if i['active'] == True]
            return channels
        else:
            print('Either you don\'t have channels selected to monitor or something went wrong')
    

    def check_if_channel_is_live(self, channel_name):
        user = self.get_twitch_user(channel_name)
        if user is not None:
            # print(f'Checking if {channel_name} is live')
            header = {'Client-Id': self.client_id, 'Authorization': f'Bearer {self.bearer}'}
            url = f"{self.TwitchBaseUrl}streams?user_id={user}"
            response = requests.get(url, headers=header)
            if response.status_code < 300:
                if len(response.json()['data']) > 0:
                    return response.json()['data'][0]
        return None

    
    # execute IRC commands
    # execute IRC commands
    def irc_command(self, command: str):
        print(f"IRC Commands -- {command}\r\n")
        self.irc.send((command + "\r\n").encode())


    # send privmsg's, which are normal chat messages
    def send_message(self, channel: str, message: str):
        self.irc_command(f"PRIVMSG #{channel} :{message}")



    # decode incoming messages
    def check_for_messages(self):
        print('Checking for messages')
        while True:
            messages = self.irc.recv(1024).decode()

            # respond to pings from Twitch
            if messages.startswith("PING"):
                self.channel = self.get_channels_to_monitor()
                print('PING RECEIVED')
                self.irc_command("PONG :tmi.twitch.tv")

            for m in messages.split("\r\n"):
                if m.strip() != '':
                    # print('--Start Message Processing--')
                    self.parse_message(m)


    # check for command being executed
    def parse_message(self, message: str):
        try:
            if 'JOIN' in message:
                return
            
            regex = """@badge-info=(?P<badge_info>([\w\/\d\0]+|));badges=(?P<badges>([\w\/\d,]{1,})|);.*;display-name=(?P<display_name>[\w]+);emotes=(?P<emotes>([\w\/\d:\-]+)|).*id=(?P<message_id>[\w\-\d]+);mod=(?P<mod>\d+);.*room-id=(?P<room_id>\d+);subscriber=(?P<subscriber>\d+);.*user-id=(?P<user_id>\d+);.*PRIVMSG\s#(?P<room_name>[\w\-\d]+)\s:(?P<message>[@#\-\$A-Za-z0-9].*[^;])$"""
            # print(message)
            pat_message = re.compile(regex, flags=re.IGNORECASE)

            details = pat_message.search(message)
            if details is not None:
                details = details.groupdict()
            else:
                if f"{self.user_name} = " in message or 'CAP * ACK' in message:
                    return
                c = re.compile('id=(?P<message_id>.*);\w.*room-id=(?P<room_id>.*);\w;.*user-id=(?P<user_id>.*);.*PRIVMSG\s#(?P<room_name>.*\w)\s:(?P<message>[@#\$A-Za-z0-9].*)$', flags=re.IGNORECASE)
                d = c.search(message).groupdict()
                user = self.get_user(d['user_id'])
                room = self.get_room(d['room_name'], d['room_id'])
                message_id = d['message_id']
                print('Failed Message:', message)
                self.store_message_data(user, room, d['message'], message_id)
                return

            user = self.get_user(details['user_id'], details['display_name'])
            room = self.get_room(details['room_name'].strip('#'), int(details['room_id']))
            print(f'Message: {details["room_name"]} - {details["display_name"]}: {details["message"]}\n')
            message = details['message']
            self.message_trigger += 1
            # check for commands being used
            check = message.startswith(f"{self.bot_trigger}")
            if message.startswith(f"{self.bot_trigger}"):
                command = details['message'].replace(self.bot_trigger, '').split()[0].lower()
                print('TextCommand Request: {} by user {}'.format(command, user))
                if command not in self.text_commands and command not in self.commands:
                    self.store_wrong_command(user, command)
                else:
                    self.execute_command(details['user_id'], details['room_name'], command, message)
            
            self.store_message_data(user, room, details['message'], details['message_id'])
            if self.message_trigger == 15:
                self.reload_text_commands()
                self.connect_to_channel()
                self.message_trigger = 0 

        except AttributeError:
            pass

    
    def get_twitch_user(self, username):
        # print('Getting Twitch User:', username)
        url=f'{self.TwitchBaseUrl}users?login=' + username
        header = {
            'client-id': self.client_id,
            'Authorization': f"Bearer {self.bearer}"
        }
        response = requests.get(url, headers=header)
        if response.status_code >= 200 and response.status_code < 300:
            if len(response.json()['data']) > 0:
                # print('UserId:', response.json()['data'][0]['id'])
                return response.json()['data'][0]['id']
            # print('User Not Found', response.json())
        return 
    
   
    def get_user(self, user_id, username):
        response = requests.get(f'{DJANGO_URL}/users/{user_id}/')
        if response.status_code == 404:
            # print(f'Adding New User since no user_id was found for: {user_id}')
            response = requests.post(f'{DJANGO_URL}/users/', data={'user_id': user_id, 'username': username})
            if response.status_code < 300:
                user = response.json()
            # else:
                # print('Failed Add User:', response.status_code)
        else:
            user = response.json()
        # print('USER:', user)
        return user


    def get_room(self, room_name, room_id):
        # print(room_name, room_id)
        response = requests.get(f'{DJANGO_URL}/rooms/{room_name}/')
        if response.status_code < 300:
            # print(response.json())
            return response.json()['id']
        else:
            data={'room_id': room_id, 'name': room_name}
            response = requests.post(f'{DJANGO_URL}/rooms/', data=data)
            if response.status_code < 300:
                return response.json()['id']
            raise BaseException(f'Failed to create a room {room_name}: ', response.status_code)
        

    # store data on commands attempted that don't exist
    def store_wrong_command(self, user: str, command: str):
        data = {'user': user['user_id'], 'command': command }
        response = requests.post(f"{DJANGO_URL}/false-commands/", data=data)
        if response.status_code> 300:
            raise BaseException('False Command failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_message_data(self, user: str, room:str, message: str, message_id: int):
        data = {'user':user['user_id'],'message': message, 'room': room, 'twith_id': message_id}
        # print('Creating Message :', data)
        response = requests.post(f"{DJANGO_URL}/messages/", data=data)
        if response.status_code> 300:
            raise BaseException('Message failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_command_data(self, user: int, command: str, is_custom: int):
        data={"user":user , "command": command, "is_custom": bool(is_custom)}
        response = requests.post(f'{DJANGO_URL}/command-usage/', data=data)
        if response.status_code> 300:
            raise BaseException('Command failed to submit: {}'.format(data))

   
    # execute each command
    def execute_command(self, user: int, channel:str, command: str, message: str):
        # execute hard-coded command
        if command in self.commands.keys():
            self.commands[command].execute(user, message) 
            is_custom_command = 0 
            self.store_command_data(user, command, is_custom_command)

        # execute custom text commands
        elif command in self.text_commands.keys():
            print('Request to send Commnd: {}'.format(command))
            print('Response in Channel {}: {}'.format(channel, self.text_commands[command]))
            self.send_message(
                channel,
                self.text_commands[command]
            )
            is_custom_command = 1
            self.store_command_data(user, command, is_custom_command)
        
        self.text_commands = self.reload_text_commands()


    def reload_text_commands(self):
        response = requests.get(f'{DJANGO_URL}/text-commands/')
        if response.status_code> 300:
            raise BaseException(f'Fail to get commands. {response.request.url} - {response.status_code}')
        raw_commands = response.json()
        commands = {i['command']: i['message'] for i in raw_commands}
        return commands
