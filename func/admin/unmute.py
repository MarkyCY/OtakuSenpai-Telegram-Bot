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


def get_user_id(username):
    user = users.find_one({"username": username})
    if user:
        return int(user["user_id"])
    else:
        return False


def unmute_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # Verificar que el usuario que envió el mensaje es un administrador del chat
        chat_id = message.chat.id
        user_id = message.from_user.id
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            # Obtener el usuario que se quiere desmutear
            if message.reply_to_message:
                user_to_unmute = message.reply_to_message.from_user
            else:
                # Si no se responde al mensaje, buscar el usuario por su nombre de usuario
                if len(message.text.split()) < 2:
                    bot.reply_to(message, "Por favor, responde al mensaje del usuario que deseas desmutear o especifica su nombre de usuario.")
                    return
                username = message.text.split()[1]
                if username.startswith('@'):
                    username = username[1:]

                user_id = get_user_id(username)
                if user_id is False:
                    bot.reply_to(message, "El usuario no está en la base de datos. Solo puede desmutearlo haciendo Reply a un mensaje suyo o manualmente 🙁")
                else:
                    user_to_unmute = bot.get_chat_member(chat_id, user_id).user

            # Levantar la restricción del usuario
            bot.restrict_chat_member(chat_id, user_to_unmute.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)

            # Enviar mensaje de confirmación
            bot.reply_to(message, f"{user_to_unmute.first_name} ha sido desmutado.")

        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")