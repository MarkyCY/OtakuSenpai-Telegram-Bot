from pymongo import MongoClient
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


# Función para obtener el número de advertencias de un usuario
def get_warnings(user_id):
    user = users.find_one({"user_id": user_id})
    if user:
        return user["warnings"]
    else:
        return 0

# Función para incrementar el número de advertencias de un usuario
def add_warning(user_id):
    user = users.find_one({"user_id": user_id})
    if user:
        warnings = user["warnings"] + 1
        if warnings > 3:
            ban_user(user_id)
        else:
            users.update_one({"user_id": user_id}, {"$set": {"warnings": warnings}})
    else:
        users.insert_one({"user_id": user_id, "warnings": 1})

# Función para banear a un usuario
def ban_user(chat_id, user_id):
    bot.kick_chat_member(chat_id, user_id)
    pass

# Comando /warn
def warn_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # Verificar que se hizo reply a un mensaje
        if not message.reply_to_message:
            bot.send_message(message.chat.id, "Por favor, haz reply a un mensaje para usar este comando.")
            return

        # Verificar que el usuario que usa el comando no es administrador ni el creador del grupo
        user_id = message.reply_to_message.from_user.id

        chat_member = bot.get_chat_member(message.chat.id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            bot.send_message(message.chat.id, "Este comando no puede ser usado con administradores o el creador del grupo.")
            return

        # Obtener el usuario al que se hizo reply
        user_id = message.reply_to_message.from_user.id

        # Verificar si el usuario ya ha llegado al límite de advertencias
        warnings = get_warnings(str(user_id))
        if warnings >= 3:
            bot.send_message(message.chat.id, f"El usuario {message.reply_to_message.from_user.username} ya ha llegado al límite de advertencias y ha sido baneado.")
            ban_user(user_id)
            return

        # Incrementar el número de advertencias del usuario
        add_warning(str(user_id))

        # Si es la tercera advertencia, banear al usuario
        warnings = get_warnings(str(user_id))
        if warnings == 3:
            bot.send_message(message.chat.id, f"Tercera advertencia para el usuario {message.reply_to_message.from_user.username}. El usuario será baneado.")
            ban_user(message.chat.id, user_id)
        else:
            bot.send_message(message.chat.id, f"Advertencia #{warnings} para el usuario {message.reply_to_message.from_user.username}.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")