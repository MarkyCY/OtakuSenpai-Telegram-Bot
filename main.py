import os
import re
import random
import telebot
from pymongo import MongoClient
from dotenv import load_dotenv


#Other Command
from func.bot_welcome import send_welcome
from func.sticker_info import sticker_info
#Admin Command
from func.admin.warn import warn_user
from func.admin.ban import ban_user
from func.admin.unban import unban_user
from func.admin.unmute import unmute_user
from func.admin.mute import mute_user
#Api Anilist Use
from func.anilist.search_manga import show_manga
from func.anilist.search_anime import show_anime
load_dotenv()



#Conectarse a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client.otakusenpai

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)


@bot.message_handler(commands=['sticker_info'])
def send_sticker_info(message):
    sticker_info(message)

# Definimos una función que será llamada cuando ocurra un cambio en los miembros del grupo
@bot.message_handler(content_types=['new_chat_members'])
def on_chat_member_updated(message):
    # Verificamos si el objeto JSON contiene la clave "new_chat_members"
    if 'new_chat_members' in message.json:
        # Si el cambio es una nueva persona que se unió al grupo, llamamos a la función "send_welcome"
        send_welcome(message)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "I'm Alive!!!")
    print(message.from_user.username)


@bot.message_handler(commands=['info'])
def info(message):
    #Verificar si el mensaje es una respuesta a otro mensaje
    if message.reply_to_message is not None:
        #Si el mensaje es un reply a otro mensaje, obtengo los datos del usuario al que se le hizo reply
        user = message.reply_to_message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        #Envio la información del usuario y su rol en un mensaje de reply al mensaje original
        bot.reply_to(message.reply_to_message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}")
    else:
        #Si el mensaje no es una respuesta a otro mensaje, obtener los datos del usuario que envió el comando
        user = message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        bot.reply_to(message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}")


@bot.message_handler(commands=['anime'])
def anime(message):
    show_anime(message)


@bot.message_handler(commands=['manga'])
def manga(message):
    show_manga(message)

    
@bot.message_handler(commands=['ban'])
def start_ban_user(message):
    ban_user(message)


@bot.message_handler(commands=['unban'])
def start_unban_user(message):
    unban_user(message)


@bot.message_handler(commands=['warn'])
def command_warn_user(message):
    warn_user(message)


@bot.message_handler(commands=['mute'])
def command_mute_user(message):
    mute_user(message)


@bot.message_handler(commands=['unmute'])
def command_unmute_user(message):
    unmute_user(message)

#Base de datos de prueba
#"{Comamand}": ["Random Answer", "Random Answer", "Random Answer"]
db = {
    "te quiero, aki": ["Yo te quiero maaas!", "Yo te Amooooo", "Wiiiiii"],
    "akira, despierta": ["Ahhh!! Aquí estoy", "Ya!! Estoy despiertaaa!", "Wenaaaaas que hora es?"],
    "chupiti": ["Respuesta 7", "Respuesta 8", "Respuesta 9"]
}

#Creo las expresiones regulares a partir de los datos de la base de datos
pattern = re.compile("|".join(db.keys()))

@bot.message_handler(func=lambda message: pattern.search(message.text))
def triggers(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        #Esta función devuelve los triggers asignados en la base de datos con las respuestas aleatorias que sean es puro entretenimiento la base de datos usada es solo de prueba
        match = pattern.search(message.text)
        if match:
            trigger = match.group()
            response = random.choice(db[trigger])
            bot.send_message(message.chat.id, response)


if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "..."),
        telebot.types.BotCommand("/anime", "Buscar información sobre un anime"),
        telebot.types.BotCommand("/manga", "Buscar información sobre un manga"),
        telebot.types.BotCommand("/info", "Ver la información de un usuario"),
        telebot.types.BotCommand("/ban", "Banear a un Usuario"),
        telebot.types.BotCommand("/unban", "Desbanear a un Usuario")
    ])
    print('Iniciando el Bot')
    bot.infinity_polling()