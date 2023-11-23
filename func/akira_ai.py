import telebot
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def get_permissions_ai(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    if(message.chat.type == 'supergroup' or message.chat.type == 'group'):
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            if message.reply_to_message:
                if user_id == 873919300:
                    user_id = message.reply_to_message.from_user.id
                    username = message.reply_to_message.from_user.username
    
                    user = users.find_one({"user_id": user_id})
                    if user is None:
                        users.insert_one({"user_id": user_id, "username": username})
                    isAki = user.get('isAki', None)
                    print(user)
                    print(isAki)
                    if isAki is not None:
                        try:
                            users.update_one({"user_id": user_id}, {"$unset": {"isAki": ""}})
                        except Exception as e:
                            print(f"An error occurred: {e}")
                        bot.reply_to(message.reply_to_message, "Te quitaron los permisos buajaja!")
                    else:
                        try:
                            users.update_one({"user_id": user_id}, {"$set": {"isAki": True}})
                        except Exception as e:
                            print(f"An error occurred: {e}")
                        bot.reply_to(message.reply_to_message, "Wiii ya puedes hablar conmigo!")
                else:
                    bot.reply_to(message, "Solo mi padre puede usar ese comando por ahora :(")
            else:
                bot.reply_to(message, "Debe hacer reply al sujeto.")
        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")