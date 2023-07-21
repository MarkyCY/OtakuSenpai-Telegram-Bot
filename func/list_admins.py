import telebot
import os

from dotenv import load_dotenv
load_dotenv()

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
        # crea una lista vacía para los nombres de los administradores (ignorando los bots)
        admin_names = []
        # itera sobre la lista de administradores y agrega los nombres de los que no son bots a la lista
        for admin in admins:
            if not admin.user.is_bot:
                admin_names.append(admin.user)
        # envía un mensaje con la lista de administradores al chat
        bot.send_message(chat_id, f"Los administradores de {chat_info.title} son:\n" + "\n".join([f'<a href="https://t.me/{user.username}">{user.first_name}</a>' for user in admin_names]), parse_mode='html', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")