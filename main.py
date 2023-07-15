import os
import re
import random
import telebot
from telebot.types import ChatMemberUpdated
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from func.api_anilist import search_anime, search_manga
from func.bot_welcome import send_welcome
from func.sticker_info import sticker_info
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
    cid = message.chat.id
    if len(message.text.split('/anime ')) > 1:
        referral_all = message.text.split(" ")
        anime_name = " ".join(referral_all[1:])
        anime = search_anime(anime_name)
        if 'errors' in anime:
            for error in anime['errors']:
                match error['message']:
                    case "Not Found.":
                        bot.send_message(message.chat.id, f"Anime no encontrado 🙁")
                    case _:
                        bot.send_message(message.chat.id, error['message'])
        else:
            name = anime['data']['Media']['title']['english']
            if (name is None):
                name = anime['data']['Media']['title']['romaji']

            duration = anime['data']['Media']['duration']
            episodes = anime['data']['Media']['episodes']
            status = anime['data']['Media']['status']
            isAdult = anime['data']['Media']['isAdult']
            match isAdult:
                case True:
                    adult = "Si"
                case False:
                    adult = "No"
                case _:
                    adult = "Desconocido"

            html_regex = re.compile(r'<[^>]+>')
            description = re.sub(html_regex, '', anime['data']['Media']['description'])[:500]
            image = anime['data']['Media']['coverImage']['large']
            res = requests.get(image)
            print(res.status_code, cid)
            with open("./file/" + name + ".jpg", 'wb') as out:
                out.write(res.content)
            foto = open("./file/" + name + ".jpg", "rb")

            msg = f"""
<strong>{name}</strong> 
<strong>Duración de cada Cap:</strong> {duration} min
<strong>Episodios:</strong> {episodes}

<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}
"""
            bot.send_photo(cid, foto, msg, parse_mode="html")
    else:
        bot.send_message(message.chat.id, f"Debes poner el nombre del anime luego de /anime")




@bot.message_handler(commands=['manga'])
def manga(message):
    cid = message.chat.id
    if len(message.text.split('/manga ')) > 1:
        referral_all = message.text.split(" ")
        manga_name = " ".join(referral_all[1:])
        manga = search_manga(manga_name)
        if 'errors' in manga:
            for error in manga['errors']:
                match error['message']:
                    case "Not Found.":
                        bot.send_message(message.chat.id, f"Manga no encontrado 😣")
                    case _:
                        bot.send_message(message.chat.id, error['message'])
        else:
            name = manga['data']['Media']['title']['english']
            if (name is None):
                name = manga['data']['Media']['title']['romaji']

            status = manga['data']['Media']['status']
            isAdult = manga['data']['Media']['isAdult']
            match isAdult:
                case True:
                    adult = "Si"
                case False:
                    adult = "No"
                case _:
                    adult = "Desconocido"

            html_regex = re.compile(r'<[^>]+>')
            description = re.sub(html_regex, '', manga['data']['Media']['description'])

            image = manga['data']['Media']['coverImage']['large']
            res = requests.get(image)
            print(res.status_code, cid)
            with open("./file/" + name + ".jpg", 'wb') as out:
                out.write(res.content)
            foto = open("./file/" + name + ".jpg", "rb")

            msg = f"""
<strong>{name}</strong> 
<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}
"""
        
            bot.send_photo(cid, foto, msg, parse_mode="html")
    else:
        bot.send_message(message.chat.id, f"Debes poner el nombre del manga luego de /manga")

    
@bot.message_handler(commands=['ban'])
def ban_user(message):
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


@bot.message_handler(commands=['unban'])
def unban_user(message):
    # obtén el ID del chat
    chat_id = message.chat.id

    # verifica si el usuario que envió el mensaje es un administrador o el creador del chat
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status in ['administrator', 'creator']:
        # verifica si se hizo reply a un mensaje
        if message.reply_to_message:
            # obtén el ID del usuario que envió el mensaje
            user_id = message.reply_to_message.from_user.id

            # verifica si el usuario ya ha sido desbaneado
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.is_member:
                # envía un mensaje de confirmación
                bot.reply_to(message, "El usuario no estaba baneado.")
            else:
                # verifica si el usuario que se quiere desbanear es un administrador
                if chat_member.status not in ['administrator', 'creator']:
                    # desbanear al usuario
                    bot.unban_chat_member(chat_id, user_id)

                    # envía un mensaje de confirmación
                    bot.reply_to(message, "Usuario desbaneado.")
                else:
                    # envía un mensaje de error si se intenta desbanear a un administrador
                    bot.reply_to(message, "No puedes desbanear a un administrador.")
        else:
            # verifica si se ingresó el nombre de usuario
            if len(message.text.split()) > 1:
                # obtén el nombre de usuario ingresado
                username = message.text.split()[1]

                # obtén información sobre el usuario
                user = bot.get_chat_member(chat_id, username).user

                # verifica si el usuario ya ha sido desbaneado
                chat_member = bot.get_chat_member(chat_id, user.id)
                if chat_member.is_member:
                    # envía un mensaje de confirmación
                    bot.reply_to(message, "El usuario no estaba baneado.")
                else:
                    # verifica si el usuario que se quiere desbanear es un administrador
                    if chat_member.status not in ['administrator', 'creator']:
                        # desbanear al usuario
                        bot.unban_chat_member(chat_id, user.id)

                        # envía un mensaje de confirmación
                        bot.reply_to(message, "Listo el usuario puede entrar cuando quiera.")
                    else:
                        # envía un mensaje de error si se intenta desbanear a un administrador
                        bot.reply_to(message, "No puedes usar este comando con un administrador.")
            else:
                # envía un mensaje de ayuda si no se hizo reply a un mensaje ni se ingresó el nombre de usuario
                bot.reply_to(message, "Debes hacer reply a un mensaje o ingresar el nombre de usuario para poder desbanear al usuario. Por ejemplo: /unban <nombre_de_usuario>")
    else:
        # envía un mensaje de error si el usuario no tiene los permisos necesarios
        bot.reply_to(message, "Debes ser administrador o el creador del chat para ejecutar este comando.")



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