from pymongo import MongoClient
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def ban_user(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        #verifica si el usuario que envió el mensaje es un administrador o el creador del chat
        chat_id = message.chat.id
        user_id = message.from_user.id
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            #verifica si se hizo reply a un mensaje
            if message.reply_to_message:
                #obtén el ID del chat y del usuario que envió el mensaje
                chat_id = message.chat.id
                user_id = message.reply_to_message.from_user.id
                user_name = message.reply_to_message.from_user.username

                #verifica si el usuario que envió el mensaje es distinto al que se quiere banear
                if user_id != message.from_user.id:
                    #obtén información sobre el usuario que se quiere banear
                    chat_member = bot.get_chat_member(chat_id, user_id)

                    #verifica si el usuario que se quiere banear es un administrador
                    if chat_member.status not in ['administrator', 'creator']:
                        #banear al usuario
                        bot.kick_chat_member(chat_id, user_id)

                        #envía un mensaje de confirmación
                        bot.reply_to(message, "Baneado! Fue bueno mientras duró.")
                        bot.reply_to(message, "A quien quiero engañar... Buajajaja!")
                    else:
                        #envía un mensaje de error si se intenta banear a un administrador y una bromita para el pana :)
                        if(user_name == "YosvelPG"):
                            bot.reply_to(message, "No puedes banear a un furro calvo y además admin. Aunque a mi papá si le gustaría...")
                        else:
                            bot.reply_to(message, "No puedes banear a otro administrador, estás loco o qué?.")
                else:
                    #envía un mensaje de error si el usuario intenta banearte a ti mismo
                    bot.reply_to(message, "No te puedes banear a ti mismo pirado!")
            else:
                #envía un mensaje de error si no se hizo reply a un mensaje
                bot.reply_to(message, "Oye si no haces Reply a un mensaje no puedo hacer mucho.")
        else:
            #envía un mensaje de error si el usuario no tiene los permisos necesarios
            bot.reply_to(message, "Debes ser administrador o el creador del grupo para ejecutar este comando. Simple mortal hump!")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")