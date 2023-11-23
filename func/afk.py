import telebot
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def set_afk(message):
    user_id = message.from_user.id
    args = message.text.split(None, 1)
    notice = ""
    
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nSu motivo de afk se redujo a 100 caracteres."
    else:
        reason = ""

    # Actualizar MongoDB
    users.update_one(
        {"user_id": user_id},
        {"$set": {"is_afk": True, "reason": reason}},
        upsert=True
    )

    fname = message.from_user.first_name
    res = "{} ahora está AFK!{}".format(fname, notice)
    bot.reply_to(message, res)