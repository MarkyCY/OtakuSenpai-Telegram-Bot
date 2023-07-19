import telebot
import datetime
import os
import re

from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


def get_user_id(username):
    user = users.find_one({"username": username})
    if user:
        return int(user["user_id"])
    else:
        return False
    
def add_ban(user_id, username):
    user = users.find_one({"user_id": user_id})
    if user:
        pass
    else:
        users.insert_one({"user_id": user_id, "username": username})

def ban_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # Verificar que el usuario que envió el mensaje es un administrador del chat
        chat_id = message.chat.id
        user_id = message.from_user.id
        username = message.from_user.username
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            
            # Obtener el usuario que se quiere banear
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                chat_member = bot.get_chat_member(message.chat.id, user_id)                

                user_to_ban = bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                if len(message.text.split()) > 1:
                    reason = message.text.split()[1]
                    match = re.match(r'^(\d+)([dhm])$', reason)
                    if match:
                        num = int(match.group(1))
                        unit = match.group(2)
                        if unit == 'h':
                            until_date = int((datetime.datetime.now() + datetime.timedelta(hours=num)).timestamp())
                        elif unit == 'd':
                            until_date = int((datetime.datetime.now() + datetime.timedelta(days=num)).timestamp())
                        elif unit == 'm':
                            until_date = int((datetime.datetime.now() + datetime.timedelta(minutes=num)).timestamp())
                    else:
                        print("El formato del tiempo es inválido.")
                        until_date = None
                else:
                    until_date = None
            else:
                if len(message.text.split()) > 1:
                    target = message.text.split()[1]
                    try:
                        time = message.text.split()[2]
                    except IndexError:
                        time = None
                    if time is not None:
                        match_duration = re.match(r'^(\d+)([dhm])$', time)
                    else:
                        match_duration = None
                    match_user = re.match(r'^@(\w+)$', target)
                    match_id = re.match(r'^(\d+)$', target)
                    if match_user:
                        if get_user_id(match_user.group(1)) is not False:
                            user_to_ban = bot.get_chat_member(chat_id, get_user_id(match_user.group(1)))
                        else:
                            bot.reply_to(message, "El usuario no está registrado en la base de datos.")
                            return
                    elif match_id:
                        user_to_ban = bot.get_chat_member(chat_id, int(match_id.group(1)))
                    if match_duration:
                        if len(message.text.split()) > 2:
                            num = int(match_duration.group(1))
                            unit = match_duration.group(2)
                            if unit == 'h':
                                until_date = int((datetime.datetime.now() + datetime.timedelta(hours=num)).timestamp())
                            elif unit == 'd':
                                until_date = int((datetime.datetime.now() + datetime.timedelta(days=num)).timestamp())
                            elif unit == 'm':
                                until_date = int((datetime.datetime.now() + datetime.timedelta(minutes=num)).timestamp())
                        else:
                            print("El formato del objetivo es inválido.")
                            until_date = None
                    else:
                        until_date = None
                else:
                    until_date = None


            if user_to_ban.status in ['administrator', 'creator']:
                bot.send_message(message.chat.id, "Este comando no puede ser usado con administradores o el creador del grupo.")
                return
            
            user_to_ban = user_to_ban.user
            user_id = user_to_ban.id
            username = user_to_ban.username
            add_ban(str(user_id), username)

            # Banear al usuario
            bot.kick_chat_member(chat_id, user_to_ban.id, until_date=until_date)
            
            # Enviar mensaje de confirmación
            if until_date:
                match unit:
                    case "d":
                        unit = "día(s)"
                    case "h":
                        unit = "hora(s)"
                    case "m":
                        unit = "minuto(s)"

                bot.reply_to(message, f"{user_to_ban.first_name} ha sido baneado por {num} {unit}.")
            else:
                bot.reply_to(message, f"{user_to_ban.first_name} ha sido baneado indefinidamente.")

        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")