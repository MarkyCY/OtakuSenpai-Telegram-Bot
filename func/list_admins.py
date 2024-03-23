import telebot
import os
from database.mongodb import get_db

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
db = get_db()
chat_admins = db.admins


#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def list_admins(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # obtén la información del chat
        chat_id = message.chat.id
        #chat_info = bot.get_chat(chat_id)
        # obtén la lista de administradores del chat
        admins = bot.get_chat_administrators(chat_id)

        # Divide a los administradores en propietario y otros administradores
        owner = None
        other_admins = []

        for admin in admins:
            if admin.status == 'creator':
                owner = admin
            elif not admin.user.is_bot:
                other_admins.append(admin)
                # guarda el administrador en la base de datos si no existe
                #if chat_admins.find_one({"user_id": admin.user.id}) is None:
                #    chat_admins.insert_one({"user_id": admin.user.id, "username": admin.user.username})

        # envía un mensaje con la lista de administradores al chat
        message_text = f"👑Propietario:\n└ <a href='https://t.me/{owner.user.username}'>{owner.user.username} > {owner.custom_title}</a>\n\n⚜️ Administradores:"
        
        for user in other_admins[:-1]:
            message_text += f"\n├ <a href='https://t.me/{user.user.username}'>{user.custom_title}</a>"

        if other_admins:
            message_text += f"\n└ <a href='https://t.me/{other_admins[-1].user.username}'>{other_admins[-1].custom_title}</a>"

        bot.send_message(chat_id, message_text, parse_mode='html', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, "Este comando solo puede ser usado en grupos y en supergrupos")



def isAdmin(user_id):
    isAdmin = None
    admins = chat_admins.find()
    for admin in admins:
        if admin['user_id'] == user_id:
            isAdmin = "Yes"
    return isAdmin