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
    bot_thread = threading.Thread(target=my_bot.run)
    notificator_thread = threading.Thread(target=notificator.run) 
    bot_thread.start()
    notificator_thread.start()
    bot_thread.join()
    notificator_thread.join()