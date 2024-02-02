import telebot
import datetime
import os

from telebot.apihelper import ApiTelegramException

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
users = db.users

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)



def calvicia(uid, seconds):
    try:
        bot.send_message(uid, f"Ha(n) pasado {seconds} segundo(s)")
    except ApiTelegramException as err:
        print(err)