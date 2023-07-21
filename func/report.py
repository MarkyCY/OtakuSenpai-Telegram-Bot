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
        chat_id = message.chat.id

        chat_member = bot.get_chat_member(chat_id, message.from_user.id)
        if chat_member.status in ['administrator', 'creator']:
            bot.send_message(message.chat.id, f"Este comando no está disponible para administradores")
            return
        
        if message.reply_to_message:
            chat_str_id = str(message.chat.id)[4:]
            message_id = message.reply_to_message.message_id
            # obtén la lista de administradores del chat
            admins = bot.get_chat_administrators(chat_id)
            # crea una lista vacía para los nombres de los administradores (ignorando los bots)
            admin_names = []
            # itera la lista de administradores y envia report a cada uno con el mensaje
            for admin in admins:
                if not admin.user.is_bot:
                    admin_names.append(admin.user)
                    try:
                        bot.send_message(admin.user.id, f"Reporte de @{message.from_user.username} a @{message.reply_to_message.from_user.username}:\n" + f'<a href="https://t.me/c/{chat_str_id}/{message_id}">https://t.me/c/{chat_str_id}/{message_id}</a>', parse_mode="html")
                        bot.forward_message(admin.user.id, message.chat.id, message_id)
                    except telebot.apihelper.ApiTelegramException as e:
                        print(f"No se pudo enviar el mensaje a {admin.user.username}: {e}")
                        continue
        else:
            bot.send_message(message.chat.id, f"Debes hacer reply a un mensaje para poder reportar a un usuario")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")