import telebot
import datetime
import os
import re

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


def get_user_id(username):
    user = users.find_one({"username": username})
    if user:
        return int(user["user_id"])
    else:
        return False
    
def add_ban(user_id, username):
    user = users.find_one({"user_id": user_id})
    if user:
        pass
    else:
        users.insert_one({"user_id": user_id, "username": username})

def ban_user(message):
    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_member = bot.get_chat_member(message.chat.id, user_id)                
        user_to_ban = bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        reason = message.text.split()[1] if len(message.text.split()) > 1 else None
    else:
        target = message.text.split()[1] if len(message.text.split()) > 1 else None
        time = message.text.split()[2] if len(message.text.split()) > 2 else None
        match_user = re.match(r'^@(\w+)$', target) if target else None
        match_id = re.match(r'^(\d+)$', target) if target else None
        match_duration = re.match(r'^(\d+)([dhm])$', time) if time else None
        reason = match_duration.group(0) if match_duration else None

    if not reason:
        print("El formato del tiempo es inválido.")
        until_date = None
    else:
        match = re.match(r'^(\d+)([dhm])$', reason)
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'h':
            until_date = int((datetime.datetime.now() + datetime.timedelta(hours=num)).timestamp())
        elif unit == 'd':
            until_date = int((datetime.datetime.now() + datetime.timedelta(days=num)).timestamp())
        elif unit == 'm':
            until_date = int((datetime.datetime.now() + datetime.timedelta(minutes=num)).timestamp())

    if user_to_ban.status in ['administrator', 'creator']:
        bot.send_message(message.chat.id, "Este comando no puede ser usado con administradores o el creador del grupo.")
        return

    user_to_ban = user_to_ban.user
    user_id = user_to_ban.id
    username = user_to_ban.username
    add_ban(str(user_id), username)

    bot.kick_chat_member(chat_id, user_to_ban.id, until_date=until_date)

    if until_date:
        match unit:
            case "d":
                unit = "día(s)"
            case "h":
                unit = "hora(s)"
            case "m":
                unit = "minuto(s)"

        bot.reply_to(message, f"{user_to_ban.first_name} ha sido baneado por {num} {unit}.")
    else:
        bot.reply_to(message, f"{user_to_ban.first_name} ha sido baneado indefinidamente.")