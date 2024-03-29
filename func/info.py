import telebot
import os

from dotenv import load_dotenv
from database.mongodb import get_db
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

# Conectar a la base de datos
db = get_db()
users = db.users

def info(message):
    #Verificar si el mensaje es una respuesta a otro mensaje
    if message.reply_to_message is not None:
        #Si el mensaje es un reply a otro mensaje, obtengo los datos del usuario al que se le hizo reply
        user = message.reply_to_message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        user_db = users.find_one({"user_id": user.id})
        description = user_db.get('description', '-')
        #Envio la información del usuario y su rol en un mensaje de reply al mensaje original
        bot.reply_to(message.reply_to_message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}\nDescripción: {description}")
    else:
        #Si el mensaje no es una respuesta a otro mensaje, obtener los datos del usuario que envió el comando
        user = message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        bot.reply_to(message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}")
