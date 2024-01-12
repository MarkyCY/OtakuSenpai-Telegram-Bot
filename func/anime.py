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
    if len(args) < 2:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque no se ha proporcionado un título.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque no se ha respondido a ningún mensaje.")
        return

    if message.reply_to_message.forum_topic_created is not None:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el mensaje es un tema del foro.")
        return

    chat_username = message.chat.username
    if chat_username is None:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el chat no tiene un nombre de usuario.")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        bot.reply_to(message, "Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return

    message_id = message.reply_to_message.id
    topic_id = message.message_thread_id if message.is_topic_message else None
    if not topic_id or topic_id != 251973:
        bot.reply_to(message, "Este comando solo puede ser usado en el tópico de <a href='https://t.me/OtakuSenpai2020/251973'>Anime</a>", parse_mode="HTML")
        return

    text = f"Título: {args[1]} \nEnlace: https://t.me/{chat_username}/{topic_id}/{message_id}"
    print(text)
    link = f"https://t.me/{chat_username}/{topic_id}/{message_id}"
    
    is_anime = animes.find_one({"link": link})
    if is_anime is not None:
        bot.reply_to(message, "Este link ya fue registrado")
        return

    try:
        animes.insert_one({"title": args[1], "link": link})
    except Exception as e:
        bot.reply_to(message, f"Error al registrar anime en la base de datos: {e}")
        return

    msg = bot.reply_to(message, text)
    time.sleep(5)
    bot.delete_message(msg.chat.id, msg.message_id)
    
def del_anime(message):
    if not message.reply_to_message:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque no se ha respondido a ningún mensaje.")
        return

    if message.reply_to_message.forum_topic_created is not None:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el mensaje es un tema del foro.")
        return

    chat_username = message.chat.username
    if chat_username is None:
        bot.reply_to(message, "No se puede obtener el enlace del mensaje porque el chat no tiene un nombre de usuario.")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        bot.reply_to(message, "Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return

    message_id = message.reply_to_message.id
    topic_id = message.message_thread_id if message.is_topic_message else None
    if not topic_id or topic_id != 251973:
        bot.reply_to(message, "Este comando solo puede ser usado en el tópico de <a href='https://t.me/OtakuSenpai2020/251973'>Anime</a>", parse_mode="HTML")
        return

    link = f"https://t.me/{chat_username}/{topic_id}/{message_id}"
    is_anime = animes.find_one({"link": link})
    if is_anime is None:
        bot.reply_to(message, "Este anime no existe en la base de datos.")
        return

    try:
        animes.delete_one({"link": link})
    except Exception as e:
        bot.reply_to(message, f"Error al eliminar anime en la base de datos: {e}")
        return

    msg = bot.reply_to(message, "Anime eliminado correctamente.")
    time.sleep(5)
    bot.delete_message(msg.chat.id, msg.message_id)
