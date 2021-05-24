import os
import re
import socket
import command
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("./credentials.env")

DJANGO_URL = "http://backend:8000/api"


class Bot():
    def __init__(self):
        self.server = "irc.twitch.tv"
        self.port = 6667
        self.oauth_token = os.getenv('OAUTH_TOKEN')
        self.bot_name = os.getenv('BOT_NAME')
        self.channel = ' #'.join(os.getenv('CHANNEL').split(','))
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.bearer = self.get_bearer()
        self.user_name = os.getenv('USERNAME')
        self.bot_trigger = os.getenv('BOT_TRIGGER')
        # self.user_id = self.get_twitch_user(self.user_name)['data'][0]['id']
        self.commands = {s.command_name: s for s in (c(self) for c in command.CommandBase.__subclasses__())}
        self.text_commands = self.reload_text_commands()
        self.DJANGO_URL = DJANGO_URL

    def get_bearer(self) -> str:
        print('Getting Bearer')
        print('CLIENT_ID:', self.client_id)
        print('CLIENT_Secret:', self.client_secret)
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
        self.irc_command(f"NICK flyboy1565")
        self.irc_command(f"JOIN #{self.channel}")
        self.irc_command(f"CAP REQ :twitch.tv/tags")        
        # self.send_message(self.channel, "Hello!")
        self.check_for_messages()

    
    # execute IRC commands
    def irc_command(self, command: str):
        print(f'IRC - {command} :', self.irc.send((command + "\r\n").encode()))


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
                self.irc_command("PONG :tmi.twitch.tv")

            #Todo: Add Autoban Here
            #Todo: Autoban auto remove message            sprint(messages)
                
            for m in messages.split("\r\n"):
                print('Message --:', m)
                self.parse_message(m)


    # check for command being executed
    def parse_message(self, message: str):
        try:
            # regex pattern
            if 'client-nonce' in message:
                regex = "@badge-info=(?P<badge_info>.*);badges=(?P<badges>.*);client-nonce=.*;.*display-name=(?P<display_name>.*);em.*;id=(?P<message_id>.*);mod=(?P<mod>\d);room-id=(?P<room_id>.*);subscriber=(?P<subscriber>\d+);.*user-id=(?P<user_id>\d+);user-type=(?P<user_type>.*)\sPRIVMSG\s(?P<room_name>.*)\s:(?P<message>.*)"
            else:
                regex = "@badge-info=(?P<badge_info>.*);badges=(?P<badges>.*);color=.*;.*display-name=(?P<display_name>.*);em.*;id=(?P<message_id>.*);mod=(?P<mod>\d);room-id=(?P<room_id>.*);subscriber=(?P<subscriber>\d+);.*user-id=(?P<user_id>\d+);user-type=(?P<user_type>.*)\sPRIVMSG\s(?P<room_name>.*)\s:(?P<message>.*)"
            

            pat_message = re.compile(regex, flags=re.IGNORECASE)

            try:
                details = pat_message.search(message).groupdict()
            except AttributeError:
                c = re.compile('PRIVMSG\s(?P<room_name>.*)\s:', flags=re.IGNORECASE)
                room = c.search(message).groupdict()
                u = re.compile('user-id=(?P<user_id>\d+);', flags=re.IGNORECASE)
                user = u.search(message).groupdict()
                self.send_message(self.channel, room['room_name'], user['user_id'])
                return

            print(f'{details["message_id"]} - {details["display_name"]}: {details["message"]}')
        
            # respond to server pings
            if message.lower().startswith("ping"):
                print("ping received")
                self.irc_command("PONG")
                print("pong sent")
            user = self.get_user(details['user_id'], details['display_name'])
            # check for commands being used
            if message.startswith("{self.bot_trigger}"):
                command = details['message'].split()[0].lower()
                if command not in self.text_commands and command not in self.commands:
                    self.store_wrong_command(user, command)
                else:
                    self.execute_command(user['username'], command, message)
            
            self.store_message_data(user,details['room_name'], details['message'])

        except AttributeError:
            pass

    
    def get_twitch_user(self, username):
        print('Getting Twitch User:', username)
        url='https://api.twitch.tv/helix/users?login=' + username
        header = {
            'client-id': self.client_id,
            'Authorization': f"Bearer {self.bearer}"
        }
        print("Running Url:", url)
        print('With Header:', header)
        response = requests.get(url, headers=header)
        print('Got Response:', response.status_code)
        if response.status_code >= 200 and response.status_code< 300:
            print(response.json())
            return response.json()
        return 
    
   
    def get_user(self, user_id, username):
        response = requests.get(f'{DJANGO_URL}/users/{user_id}/')
        if response.status_code == 404:
            print(f'Adding New User since no user_id was found for: {user_id}')
            response = requests.post(f'{DJANGO_URL}/users/', data={'user_id': user_id, 'username': username})
            if response.status_code < 300:
                user = response.json()
            else:
                print('Failed Add User:', response.status_code)
        else:
            user = response.json()
        print('USER:', user)
        return user

    # store data on commands attempted that don't exist
    def store_wrong_command(self, user: str, command: str):
        data = {'user': user['user_id'], 'command': command }
        response = requests.post(f"{DJANGO_URL}/false-commands/", data=data)
        if response.status_code> 300:
            raise BaseException('False Command failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_message_data(self, user: str, room:str, message: str):
        data = {'user':user['user_id'],'message': message, 'room': room}
        print('Creating Message:', data)
        response = requests.post(f"{DJANGO_URL}/messages/", data=data)
        if response.status_code> 300:
            raise BaseException('Message failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_command_data(self, user: str, command: str, is_custom: int):
        params = {'user':user['user_id'],'command': command, 'is_custom': bool(is_custom)}
        response = request.post(f'{DJANGO_URL}/command-usage/', data=params)
        if response.status_code> 300:
            raise BaseException('Command failed to submit: {}'.format(params))

   
    # execute each command
    def execute_command(self, user: str, command: str, message: str):
        # execute hard-coded command
        if command in self.commands.keys():
            self.commands[command].execute(user, message) 
            is_custom_command = 0 
            self.store_command_data(user, command, is_custom_command)

        # execute custom text commands
        elif command in self.text_commands.keys():
            self.send_message(
                self.channel,
                self.text_commands[command]
            )
            is_custom_command = 1
            self.store_command_data(user, command, is_custom_command)
        
        self.text_commands = self.reload_text_commands()


    def reload_text_commands(self):
        from subprocess import getoutput
        print(f'URL : {DJANGO_URL}')
        print(f'URL : {DJANGO_URL}/text-commands/')
        # print(getoutput(f'curl {DJANGO_URL}'))
        print()
        response = requests.get(f'{DJANGO_URL}/text-commands/')
        if response.status_code> 300:
            raise BaseException(f'Fail to get commands. {response.request.url} - {response.status_code}')
        raw_commands = response.json()
        commands = {i['commands']: i['message'] for i in raw_commands}
        return commands
