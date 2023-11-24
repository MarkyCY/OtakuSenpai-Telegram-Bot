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

def set_description(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split(None, 1)
    if(message.chat.type == 'supergroup' or message.chat.type == 'group'):
        chat_member = bot.get_chat_member(chat_id, user_id)
        #if chat_member.status in ['administrator', 'creator']:
        if message.reply_to_message:
            if len(args) >= 2:
                if user_id == 873919300 or user_id == 5579842331 or user_id == 1881435398:
                    description = args[1]
                    username = message.reply_to_message.from_user.username
                    if len(description) > 100:
                        description = description[:100]
                        notice = "\nSu motivo de afk se redujo a 100 caracteres."
                    user_id = message.reply_to_message.from_user.id
                    users.update_one({"user_id": user_id}, {"$set": {"username": username, "description": description}}, upsert=True)
                    bot.reply_to(message.reply_to_message, "Descripción actualizada correctamente.")
                else:
                    bot.reply_to(message, "Solo mi padre puede usar ese comando por ahora :(")
            else:
                bot.reply_to(message, "Proporcionar una descripción para el usuario.")
        else:
            bot.reply_to(message, "Debe hacer reply para este comando.")
        #else:
            #bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")