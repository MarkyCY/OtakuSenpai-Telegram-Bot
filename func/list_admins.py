import telebot
import os
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
chat_admins = db.admins


#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def list_admins(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # obtén la información del chat
        chat_id = message.chat.id
        chat_info = bot.get_chat(chat_id)
        # obtén la lista de administradores del chat
        admins = bot.get_chat_administrators(chat_id)
        # itera sobre la lista de administradores y agrega los nombres de los que no son bots a la lista
        admin_names = []
        for admin in admins:
            if not admin.user.is_bot:
                admin_names.append(admin.user)
                # guarda el administrador en la base de datos si no existe
                if chat_admins.find_one({"user_id": admin.user.id}) is None:
                    chat_admins.insert_one({"user_id": admin.user.id, "username": admin.user.username})
        # envía un mensaje con la lista de administradores al chat
        bot.send_message(chat_id, f"Los administradores de {chat_info.title} son:\n" + "\n".join([f'<a href="https://t.me/{user.username}">{user.first_name}</a>' for user in admin_names]), parse_mode='html', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")

def isAdmin(user_id):
    isAdmin = None
    admins = chat_admins.find()
    for admin in admins:
        if admin['user_id'] == user_id:
            isAdmin = "Yes"
    return isAdmin