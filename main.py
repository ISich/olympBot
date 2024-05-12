from orm import SyncOrm
from bot import OlympBot
import os
from dotenv import load_dotenv
import asyncio
import telebot
from notificator import Notificator
import threading


if __name__ == '__main__': 
    SyncOrm.create_tables()
    SyncOrm.insert_data()
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    bot = telebot.TeleBot(token)
    my_bot = OlympBot(bot)
    notificator = Notificator(bot)
    notificator.run()
    my_bot.run()