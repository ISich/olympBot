from orm import SyncOrm
from bot import OlympBot
import os
from dotenv import load_dotenv


if __name__ == '__main__': 
    SyncOrm.create_tables()
    SyncOrm.insert_data()
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    my_bot = OlympBot(token)
    my_bot.run()