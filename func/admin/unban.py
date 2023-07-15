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

def unban_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # obtén el ID del chat
        chat_id = message.chat.id

        # verifica si el usuario que envió el mensaje es un administrador o el creador del chat
        user_id = message.from_user.id
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            # verifica si se hizo reply a un mensaje
            if message.reply_to_message:
                # obtén el ID del usuario que envió el mensaje
                user_id = message.reply_to_message.from_user.id

                # verifica si el usuario ya ha sido desbaneado
                chat_member = bot.get_chat_member(chat_id, user_id)
                if chat_member.is_member:
                    # envía un mensaje de confirmación
                    bot.reply_to(message, "El usuario no estaba baneado.")
                else:
                    # verifica si el usuario que se quiere desbanear es un administrador
                    if chat_member.status not in ['administrator', 'creator']:
                        # desbanear al usuario
                        bot.unban_chat_member(chat_id, user_id)

                        # envía un mensaje de confirmación
                        bot.reply_to(message, "Usuario desbaneado.")
                    else:
                        # envía un mensaje de error si se intenta desbanear a un administrador
                        bot.reply_to(message, "No puedes desbanear a un administrador.")
            else:
                # verifica si se ingresó el nombre de usuario
                if len(message.text.split()) > 1:
                    # obtén el nombre de usuario ingresado
                    username = message.text.split()[1]

                    # obtén información sobre el usuario
                    user = bot.get_chat_member(chat_id, username).user

                    # verifica si el usuario ya ha sido desbaneado
                    chat_member = bot.get_chat_member(chat_id, user.id)
                    if chat_member.is_member:
                        # envía un mensaje de confirmación
                        bot.reply_to(message, "El usuario no estaba baneado.")
                    else:
                        # verifica si el usuario que se quiere desbanear es un administrador
                        if chat_member.status not in ['administrator', 'creator']:
                            # desbanear al usuario
                            bot.unban_chat_member(chat_id, user.id)

                            # envía un mensaje de confirmación
                            bot.reply_to(message, "Listo el usuario puede entrar cuando quiera.")
                        else:
                            # envía un mensaje de error si se intenta desbanear a un administrador
                            bot.reply_to(message, "No puedes usar este comando con un administrador.")
                else:
                    # envía un mensaje de ayuda si no se hizo reply a un mensaje ni se ingresó el nombre de usuario
                    bot.reply_to(message, "Debes hacer reply a un mensaje o ingresar el nombre de usuario para poder desbanear al usuario. Por ejemplo: /unban <nombre_de_usuario>")
        else:
            # envía un mensaje de error si el usuario no tiene los permisos necesarios
            bot.reply_to(message, "Debes ser administrador o el creador del chat para ejecutar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")