import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(".env"))

from aiogram import Bot, Dispatcher

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)