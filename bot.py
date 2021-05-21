import os
import re
import socket
import command
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("./credentials.env")

DJANGO_URL = "http://127.0.0.1:8000/api"


class Bot():
    def __init__(self, user_name, text_commands: dict):
        self.server = "irc.twitch.tv"
        self.port = 6667
        self.oauth_token = os.getenv('OAUTH_TOKEN')
        self.bot_name = os.getenv('BOT_NAME')
        self.channel = os.getenv('CHANNEL')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.bearer = self.get_bearer()
        self.user_id = self.get_twitch_user(user_name)['data'][0]['id']
        self.commands = {s.command_name: s for s in (c(self) for c in command.CommandBase.__subclasses__())}
        self.text_commands = text_commands
        print('Initted ')

    def get_bearer(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type" : "client_credentials"
        }
        response = requests.post(url, params = params, timeout=3)
        data = response.json()
        bearer = data["access_token"]
        return bearer


    # connect to IRC server and begin checking for messages
    def connect_to_channel(self):
        print(f"Connecting to channel: {self.channel}")
        self.irc = socket.socket()
        self.irc.connect((self.server, self.port))
        self.irc_command(f"PASS oauth:{self.oauth_token}")
        self.irc_command(f"NICK {self.bot_name}")
        self.irc_command(f"JOIN #{self.channel}")        
        print("Joining Channel")
        self.send_message(self.channel, "I AM ALIVE!!")
        print('Sending Message: Im alive')
        self.check_for_messages()

    
    # execute IRC commands
    def irc_command(self, command: str):
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
                self.irc_command("PONG :tmi.twitch.tv")

            #Todo: Add Autoban Here
            #Todo: Autoban auto remove message
            print(messages)
                
            for m in messages.split("\r\n"):
                self.parse_message(m)


    # check for command being executed
    def parse_message(self, message: str):
        try:
            # regex pattern
            print('Message:', message)
            pat_message = re.compile(fr":(?P<user>.+)!.+#{self.channel} :(?P<text>.+)", flags=re.IGNORECASE)
            
            # pull user and text from each message
            user = re.search(pat_message, message).group("user")
            message = re.search(pat_message, message).group("text")

            # respond to server pings
            if message.lower().startswith("ping"):
                print("ping received")
                self.irc_command("PONG")
                print("pong sent")

            # check for commands being used
            if message.startswith("!"):
                command = message.split()[0].lower()
                if command not in self.text_commands and command not in self.commands:
                    self.store_wrong_command(user, command)
                else:
                    self.execute_command(user, command, message)
            self.store_message_data(user, message)

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
    
   
    def get_user(self, username):
        response = requests.get(f'{DJANGO_URL}/username/{username}/')
        if response.status_code == 404:
            data = self.get_twitch_user(username)
            if data:
                user_id = data['data'][0]['id']
                user_info = {
                    'username': username,
                    'user_id': user_id
                }
                response = requests.get(f'{DJANGO_URL}/users/{user_id}/')
                if response.status_code == 404:
                    print(f'Adding New User since no user_id was found for: {username}')
                    response = requests.post(f'{DJANGO_URL}/users/', data=user_info)
                else:
                    user = response.json()
            else:
                raise BaseException("Unable to find user from twitch")
        else:
            user = response.json()
        return user

    # store data on commands attempted that don't exist
    def store_wrong_command(self, user: str, command: str):
        user = self.get_user(user)
        data = {'user': user['user_id'], 'command': command }
        response = requests.post(f"{DJANGO_URL}/false-commands/", data=data)
        if response.status_code> 300:
            raise BaseException('False Command failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_message_data(self, user: str, message: str):
        user = self.get_user(user)
        data = {'user':user['user_id'],'message': message}
        response = requests.post(f"{DJANGO_URL}/messages/", data=data)
        if response.status_code> 300:
            raise BaseException('Message failed to submit: {}'.format(data))

    
    # insert data to SQLite db
    def store_command_data(self, user: str, command: str, is_custom: int):
        user = self.get_user(user)
        params = {'user':user['user_id'],'command': command, 'is_custom': bool(is_custom)}
        response = request.post(f'{DJANGO_URL}/command-usage/', data=params)
        if response.status_code> 300:
            raise BaseException('Command failed to submit: {}'.format(params))

   
    # execute each command
    def execute_command(self, user: str, command: str, message: str):
        user = self.get_user(user)['username']
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
        response = requests.get(f'{DJANGO_URL}/text-commands/')
        if response.status_code> 300:
            raise BaseException('Fail to get commands.')
        raw_commands = response.json()
        commands = {i['commands']: i['message'] for i in raw_commands}
        return commands
