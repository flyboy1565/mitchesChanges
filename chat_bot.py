import requests
import sqlite3
from sqlalchemy import select, update, insert
from bot import Bot
from datetime import datetime
from sqlalchemy import select, insert
from database import Base, Session, engine
# from models import TextCommands, BotTime 

DJANGO_URL = "http://127.0.0.1:8000/api"


def get_text_commands() -> dict:
    response = requests.get(f'{DJANGO_URL}/text-commands/')
    if response.status_code > 300:
        raise BaseException('Fail to get commands.')
    raw_commands = response.json()
    commands = {i['command']: i['message'] for i in raw_commands}
    return commands


def main():
    text_commands = get_text_commands()
    bot = Bot('flyboy1565',text_commands)
    bot.connect_to_channel()


if __name__ == "__main__":
    main()

