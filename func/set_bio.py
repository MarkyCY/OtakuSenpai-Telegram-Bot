import telebot
import os

from dotenv import load_dotenv
from database.mongodb import get_db

load_dotenv()

# Conectar a la base de datos
db = get_db()
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def set_description(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    args = message.text.split(None, 1)

    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Debe hacer reply para este comando.")
        return

    if len(args) < 2:
        bot.reply_to(message, "Proporcionar una descripción para el usuario.")
        return

    if user_id not in [873919300, 5579842331, 1881435398, 6811585914]:
        bot.reply_to(message, "Solo mi padre puede usar ese comando por ahora :(")
        return

    description = args[1]
    username = message.reply_to_message.from_user.username
    if len(description) > 100:
        description = description[:100]
        notice = "\nSu motivo de afk se redujo a 100 caracteres."

    user_id = message.reply_to_message.from_user.id
    users.update_one({"user_id": user_id}, {"$set": {"username": username, "description": description}}, upsert=True)
    bot.reply_to(message.reply_to_message, "Descripción actualizada correctamente.")