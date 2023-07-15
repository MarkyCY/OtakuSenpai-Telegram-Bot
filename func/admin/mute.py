import telebot
import datetime
import os

from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


# Función para incrementar el número de advertencias de un usuario
def add_mute(user_id, username):
    user = users.find_one({"user_id": user_id})
    if user:
        pass
    else:
        users.insert_one({"user_id": user_id, "username": username})

def mute_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # Verificar que el usuario que envió el mensaje es un administrador del chat
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            # Obtener el usuario que se quiere mutear
            if message.reply_to_message:
                user_to_mute = message.reply_to_message.from_user
            
 
            # Calcular el tiempo de la restricción
            until_date = int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())

            user_id = user_to_mute.id
            username = user_to_mute.username
            add_mute(str(user_id), username)
            # Restringir al usuario
            bot.restrict_chat_member(chat_id, user_to_mute.id, until_date=until_date, can_send_messages=False)

            # Enviar mensaje de confirmación
            bot.reply_to(message, f"{user_to_mute.first_name} ha sido silenciado por una hora.")

        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")