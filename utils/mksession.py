from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv("config.env")
API_KEY = os.environ.get("API_KEY", None)
API_HASH = os.environ.get("API_HASH", None)

bot = TelegramClient('pagermaid', API_KEY, API_HASH)
bot.start()
