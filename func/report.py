import telebot
import os

from dotenv import load_dotenv
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def report(message):
    # obtén la información del chat
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        if message.reply_to_message:
            chat_id = message.chat.id
            # obtén la lista de administradores del chat
            admins = bot.get_chat_administrators(chat_id)
            # crea una lista vacía para los nombres de los administradores (ignorando los bots)
            admin_names = []
            # itera la lista de administradores y envia report a cada uno con el mensaje
            for admin in admins:
                if not admin.user.is_bot:
                    admin_names.append(admin.user)
                    try:
                        bot.send_message(admin.user.id, f"Reporte de @{message.from_user.username} a @{message.reply_to_message.from_user.username}:\n" + message.reply_to_message.text)
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"No se pudo enviar el mensaje a {admin.user.username}: {e}")
                        continue
        else:
            bot.send_message(message.chat.id, f"Debes hacer reply a un mensaje para poder reportar a un usuario")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")