import telebot
import os
import time

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
animes = db.animes

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def add_anime(message):
    args = message.text.split(None, 1)
    if len(args) >= 2:
        if message.reply_to_message:
            if message.reply_to_message.forum_topic_created is None:
                chat_username = message.chat.username
                if chat_username is not None:
                    if chat_username == "OtakuSenpai2020":
                        message_id = message.reply_to_message.id
                        topic_id = message.message_thread_id if message.is_topic_message else None
                        if topic_id and topic_id == 251973:
                            text = f"Título: {args[1]} \nEnlace: https://t.me/{chat_username}/{topic_id}/{message_id}"
                            msg = bot.reply_to(message, text)
                            time.sleep(5)
                            bot.delete_message(msg.chat.id, msg.message_id)
                        else:
                            bot.reply_to(message, "Este comando solo puede ser usado en el tópico de <a href='https://t.me/OtakuSenpai2020/251973'>Anime</a>", parse_mode="HTML")
                    else:
                        bot.reply_to(message, "Este comando solo puede ser usado en el grupo de OtakuSenpai.")
                else:
                    bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el chat no tiene un nombre de usuario.")
            else:
                bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el mensaje es un tema del foro.")
        else:
            bot.reply_to(message, "No se puede obtener el enlace del mensaje porque no se ha respondido a ningún mensaje.")
    else:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque no se ha proporcionado un título.")
