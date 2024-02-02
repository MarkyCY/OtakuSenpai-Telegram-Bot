from pymongo import MongoClient
import telebot
import os
import re

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

# Función para obtener el ID del usuario a partir del nombre de usuario
def get_user_id(username):
    user = users.find_one({"username": username})
    if user:
        return int(user["user_id"])
    else:
        return False

# Función para obtener el número de advertencias de un usuario
def get_warnings(user_id):
    user = users.find_one({"user_id": user_id})
    if user and "warnings" in user:
        return user["warnings"]
    else:
        return 0

# Función para incrementar el número de advertencias de un usuario
def add_warning(user_id):
    user = users.find_one({"user_id": user_id})
    if user:
        if "warnings" in user:
            warnings = user["warnings"] + 1
            if warnings > 3:
                ban_user(user_id)
            else:
                users.update_one({"user_id": user_id}, {"$set": {"warnings": warnings}})
        else:
            users.update_one({"user_id": user_id}, {"$set": {"warnings": 1}})
    else:
        users.insert_one({"user_id": user_id, "warnings": 1})

# Función para banear a un usuario
def ban_user(chat_id, user_id):
    bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
    #bot.kick_chat_member(chat_id, user_id)
    users.update_one({"user_id": user_id}, {"$set": {"warnings": 0}})
    pass

# Comando /warn
def warn_user(message, to_ban=None):
    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator'] and not to_ban:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if to_ban:
        print("Mala palabra detectada")
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        if len(message.text.split()) <= 1:
            bot.reply_to(message, "Por favor, proporciona un nombre de usuario o ID válido.")
            return

        target = message.text.split()[1]
        match_user = re.match(r'^@(\w+)$', target)
        match_id = re.match(r'^(\d+)$', target)

        if match_user and get_user_id(match_user.group(1)) is not False:
            user_id = get_user_id(match_user.group(1))
        elif match_id:
            user_id = int(match_id.group(1))
        else:
            bot.reply_to(message, "El usuario no está registrado en la base de datos.")
            return

    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status in ['administrator', 'creator'] and not to_ban:
        bot.send_message(chat_id, "Este comando no puede ser usado con administradores o el creador del grupo.")
        return

    warnings = get_warnings(str(user_id))
    if warnings >= 3:
        bot.send_message(chat_id, f"El usuario {chat_member.user.username} ya ha llegado al límite de advertencias y ha sido muteado.")
        ban_user(chat_id, user_id)
        return

    add_warning(str(user_id))

    warnings = get_warnings(str(user_id))
    if warnings == 3:
        bot.send_message(chat_id, f"Tercera advertencia para el usuario {chat_member.user.username}. El usuario será muteado.")
        ban_user(chat_id, user_id)
    else:
        bot.send_message(chat_id, f"Advertencia #{warnings} para el usuario {chat_member.user.username}.")