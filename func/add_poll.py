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

def write_num(message, options):
        if message.text is not None:
            try:
                num = int(message.text)
            except ValueError:
                msg = bot.send_message(message.from_user.id, "Eso no es un número, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, write_num)
                return
            if num > len(options):
                msg = bot.send_message(message.from_user.id, "Ese número no está entre las opciones, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, write_num)
            else:
                num = int(message.text) - 1
                # Registrar la respuesta del usuario
                #users.update_one({'user_id': uid}, {'$set': {'contest.0.answer': num}})
                bot.send_message(message.from_user.id, "¡Listo! Tu respuesta ha sido registrada.")
        
