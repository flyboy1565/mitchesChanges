import requests
import random
import json
import sqlite3
from datetime import datetime
from dateutil import relativedelta, parser
from abc import ABC, abstractmethod
# from models import BotTime, Followers


class CommandBase(ABC):
    def __init__(self, bot):
        self.bot = bot
    

    @property
    @abstractmethod
    def command_name(self):
        raise NotImplementedError


    @abstractmethod
    def execute(self):
        raise NotImplementedError


    def __repr__(self):
        return self.command_name


class AddCommand(CommandBase):

    @property
    def command_name(self):
        return "{self.bot.bot_trigger}addcommand"


    def execute(self, user, message):
        if user == self.bot.channel:
            first_word = message.split()[1]
            command = first_word if first_word.startswith("{self.bot.bot_trigger}") else "{self.bot.bot_trigger}" + first_word
            result = " ".join(message.split()[2:])

            if command in self.bot.text_commands.keys():
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, @{user}."
                )
                return

            response = requests.post(f"{self.self.bot.DJANGO_URL}/text-commands/", params={'command': command, 'message':result})
            if response.status_code >= 200 and response.status_code < 300:
                self.bot.send_message(
                    self.bot.channel,
                    f"{command} added successfully{self.bot.bot_trigger}"
                )
            else:
                self.bot.send_message(
                    self.bot.channel,
                    f"Failed to add that command, @{user}."
                )


class DeleteCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}delcommand"


    def execute(self, user, message):
        if user == self.bot.channel:
            try:
                first_word = message.split()[1]
            except IndexError:
                self.bot.send_message(
                    self.bot.channel,
                    "You didn't select a command to delete{self.bot.bot_trigger}"
                )
                return

            command = first_word if first_word.startswith("{self.bot.bot_trigger}") else "{self.bot.bot_trigger}" + first_word
            
            current_commands = self.bot.reload_text_commands()
            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"The {command} command doesn't exist, @{user}."
                )
                return

            entry = {"command": command}

            response = requests.delete(f"{self.self.bot.DJANGO_URL}/text-commands/", params={'command': command})
            if response.status_code >= 200 and response.status_code < 300:
                self.bot.send_message(
                    self.bot.channel,
                    f"{self.bot.bot_trigger}{command} command deleted, @{user}."
                )


# edit existing text command
class EditCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}editcommand"


    def execute(self, user, message):
        if user == self.bot.channel:
            first_word = message.split()[1]
            command = first_word if first_word.startswith("{self.bot.bot_trigger}") else "{self.bot.bot_trigger}" + first_word


            current_commands = self.bot.reload_text_commands()
            if command not in current_commands:
                self.bot.send_message(
                    self.bot.channel,
                    f"That command doesn't exist, @{user}."
                )
                return

            new_message = " ".join(message.split()[2:])

            response = requests.put(f"{self.self.bot.DJANGO_URL}/text-commands/", params={'command': command, 'message': new_message})
            if response.status_code >= 200 and response.status_code < 300:
                self.bot.send_message(
                    self.bot.channel,
                    f"{command} command edit complete @{user}{self.bot.bot_trigger}"
                )


class JokeCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}joke"


    def execute(self, user, message):
        url = "https://icanhazdadjoke.com/"
        headers = {"accept" : "application/json"}
        for _ in range(10):
            result = requests.get(url, headers = headers).json()
            joke = result["joke"]
            if len(joke) <= 500:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = joke
                )
                break
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"I'm sorry{self.bot.bot_trigger} I couldn't find a short enough joke. :("
        )


class PoemCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}poem"


    def execute(self, user, message):
        num_lines = 4
        url = f"https://poetrydb.org/linecount/{num_lines}/lines"
        result = requests.get(url)
        poems = json.loads(result.text)
        num_poems = len(poems)
        for _ in range(5):
            idx = random.randint(0, num_poems)
            lines = poems[idx]["lines"]
            poem = "; ".join(lines)
            if len(poem) <= 500:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = poem
                )
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"@{user}, I couldn't find a short enough poem. I'm sorry. :("
        )


class CommandsCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}commands"


    def execute(self, user, message):
        text_comands = self.bot.reload_text_commands()
        hard_commands = [c.command_name for c in (s(self) for s in CommandBase.__subclasses__())]
        commands_str = ", ".join(text_commands) + ", " + ", ".join(hard_commands)

        # check if commands fit in chat; dropping
        while len(commands_str) > 500:
            commands = commands_str.split()
            commands = commands[:-2]
            commands_str = " ".join(commands)

        self.bot.send_message(
            channel = self.bot.channel,
            message = commands_str
        )


class FollowAgeCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}followage"


    def execute(self, user, message):
        if len(message.split()) > 1:
            user = message.split()[1].strip("@").lower()

        response = requests.get(f'{self.bot.DJANGO_URL}/follow-age/{user}')
        if response.status_code >= 200 and response.status_code < 300:
            follow_time = response.json()['followTime']
            follow_time = parser.parser(follow_time)

        follow_time = user_entry[0]
        now = datetime.now()

        delta = relativedelta.relativedelta(now, follow_time)
        follow_stats = {
            "year": delta.years,
            "month": delta.months,
            "day": delta.days,
            "hour": delta.hours,
            "minute": delta.minutes
        }

        message = f"{user} has been following for"
        for k,v in follow_stats.items():
            if v > 0:
                message += f" {v} {k}"
                if v > 1:
                    message += "s"
        message += "{self.bot.bot_trigger}"
        self.bot.send_message(
            channel = self.bot.channel,
            message = message
        )


class BotTimeCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}bottime"


    def execute(self, user, message):
        response  = request.get(f"{self.bot.DJANGO_URL}/bottime/last/")
        if response.status_code> 300:
            raise BaseException('Fail to get last bottime.')
    
        time = response.json()['uptime']
        uptime = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now()

        delta = relativedelta.relativedelta(now, uptime)
        uptime_stats = {
            "year": delta.years,
            "month": delta.months,
            "day": delta.days,
            "hour": delta.hours,
            "minute": delta.minutes
        }

        message = f"I have been alive for"
        for k,v in uptime_stats.items():
            if v > 0:
                message += f" {v} {k}"
                if v > 1:
                    message += "s"
        message += "{self.bot.bot_trigger}"
        self.bot.send_message(
            channel = self.bot.channel,
            message = message
        )


class RankCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}rank"


    def execute(self, user, message):
        if len(message.split()) > 1:
            command = message.split()[1]
            # command use rank
            if not command.startswith("{self.bot.bot_trigger}"):
                command = f"{self.bot.bot_trigger}{command}"

            response = requests.get(f'{self.bot.DJANGO_URL}/text-commands/')
            if response.status_code> 300:
                raise BaseException('Fail to get commands.')
            raw_commands = response.json()
            commands = [i['commands'] for i in raw_commands]

            commands = [*text_commands, *self.bot.commands] 

            if command not in commands:
                self.bot.send_message(
                        channel = self.bot.channel,
                        message = f"That is not a command that I have. Sorry{self.bot.bot_trigger}"
                    )
                return

            response = requests.get(f'{self.bot.DJANGO_URL}/rank/{user}/{command}')
            if response.status_code> 300:
                raise BaseException('Fail to get c')

            info = response.json()
            user_rank = info['rank']
            numOfUsers = info['user_count']
            message = f"{user}, you are the number {user_rank} user of the {command} command out of {numOfUsers} users."
            self.bot.send_message(
                    channel = self.bot.channel,
                    message = message
                    )

        else:
            # get count of unique chatters from chat_messages table
            response = requests.get(f'{self.bot.DJANGO_URL}/rank/{user}/')
            if response.status_code> 300:
                raise BaseException('Fail to get c')

            info = response.json()
            user_rank = info['rank']
            numOfUsers = info['user_count']

            # send the rank in chat
            message = f"{user}, you are number {user_rank} out of {numOfUsers} chatters{self.bot.bot_trigger}"
            self.bot.send_message(
                    channel = self.bot.channel,
                    message = message
                )

            
class FeatureRequestCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}featurerequest"


    def execute(self, user, message):
        params = {'user':user['user_id'],'message': message}
        response = requests.post(f'{self.bot.DJANGO_URL}/feature-requests/', data=params)
        if response.status_code> 300:
            raise BaseException('Command failed to submit: {}'.format(params))
        self.bot.send_message(
                channel = self.bot.channel,
                message = f"Got it{self.bot.bot_trigger} Thanks for your help, {user}{self.bot.bot_trigger}"
            )


class BanRequestCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}ban"


    def execute(self, user, message):
        params = {'user':user['user_id'],'message': message}
        response = requests.post(f'{self.bot.DJANGO_URL}/feature-requests/', data=params)
        if response.status_code> 300:
            raise BaseException('Command failed to submit: {}'.format(params))
        self.bot.send_message(
                channel = self.bot.channel,
                message = f"Got it{self.bot.bot_trigger} Thanks for your help, {user}{self.bot.bot_trigger}"
            )


# TODO: {self.bot.bot_trigger}lurk command to thank user for lurking with their name
class LurkCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}lurk"

    
    def execute(self, user, message):
        self.bot.send_message(
            channel = self.bot.channel,
            message = f"Don't worry {user}, we got mad love for the lurkers{self.bot.bot_trigger} <3"
        )
        

# TODO: {self.bot.bot_trigger}so command to shout out a user and link their channel
# user submitting the command can't shoutout themselves
# verify that shouted user is real
class ShoutoutCommand(CommandBase):
    @property
    def command_name(self):
        return "{self.bot.bot_trigger}so"


    def execute(self, user, message):
        # check if user shouting out no one
        if len(message.split()) < 2:
            self.bot.send_message(
                channel = self.bot.channel,
                message = f"I can't shoutout no one, {user}{self.bot.bot_trigger}"
            )

        else:
            so_user = message.split()[1].strip("@")

            # correct for users trying to shout themselves out
            if user.lower() == so_user.lower():
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"You can't shoutout yourself, {user}{self.bot.bot_trigger}"
                )
                return

            # api only returns users that have streamed in the past six months
            url = f"https://api.twitch.tv/helix/search/channels?query={so_user}"
            headers = {
                "client-id" : env.client_id,
                "authorization" : f"Bearer {env.bearer}"
            }

            response = requests.get(url, headers=headers)
            data = json.loads(response.content)["data"][0]
            so_display_name = data["display_name"]
            so_login = data["broadcaster_login"]

            # validates that user is real
            if so_user.lower() == so_login:
                so_url = f"https://twitch.tv/{so_login}"
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"Shoutout to {so_display_name}{self.bot.bot_trigger} Check them out here{self.bot.bot_trigger} {so_url}"
                )

            # user could not exist or not have streamed in 6 months
            else:
                self.bot.send_message(
                    channel = self.bot.channel,
                    message = f"{so_user} isn't a frequent streamer, {user}."
                )