from database.mongodb import get_db
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
db = get_db()
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
    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if message.reply_to_message:
        user_to_unmute = message.reply_to_message.from_user
    else:
        if len(message.text.split()) < 2:
            bot.reply_to(message, "Por favor, responde al mensaje del usuario que deseas desmutear o especifica su nombre de usuario.")
            return

        username = message.text.split()[1]
        if username.startswith('@'):
            username = username[1:]

        user_id = get_user_id(username)
        if user_id is False:
            bot.reply_to(message, "El usuario no está en la base de datos. Solo puede desmutearlo haciendo Reply a un mensaje suyo o manualmente 🙁")
            return

        user_to_unmute = bot.get_chat_member(chat_id, user_id).user

    bot.restrict_chat_member(chat_id, user_to_unmute.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
    bot.reply_to(message, f"{user_to_unmute.first_name} ha sido desmutado.")