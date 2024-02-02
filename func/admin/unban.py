from pymongo import MongoClient
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def unban_user(message):
    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Debes ser administrador o el creador del chat para ejecutar este comando.")
        return

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_member = bot.get_chat_member(chat_id, user_id)

        if chat_member.is_member:
            bot.reply_to(message, "El usuario no estaba baneado.")
            return

        if chat_member.status in ['administrator', 'creator']:
            bot.reply_to(message, "No puedes desbanear a un administrador.")
            return

        bot.unban_chat_member(chat_id, user_id)
        bot.reply_to(message, "Usuario desbaneado.")
    elif len(message.text.split()) > 1:
        username = message.text.split()[1]
        user = bot.get_chat_member(chat_id, username).user
        chat_member = bot.get_chat_member(chat_id, user.id)

        if chat_member.is_member:
            bot.reply_to(message, "El usuario no estaba baneado.")
            return

        if chat_member.status in ['administrator', 'creator']:
            bot.reply_to(message, "No puedes usar este comando con un administrador.")
            return

        bot.unban_chat_member(chat_id, user.id)
        bot.reply_to(message, "Listo el usuario puede entrar cuando quiera.")
    else:
        bot.reply_to(message, "Debes hacer reply a un mensaje o ingresar el nombre de usuario para poder desbanear al usuario. Por ejemplo: /unban <nombre_de_usuario>")