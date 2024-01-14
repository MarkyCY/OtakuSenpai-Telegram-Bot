from pymongo import MongoClient
from func.api_anilist import search_manga
from deep_translator import GoogleTranslator
from telebot.types import ReactionTypeEmoji
import requests
import re
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def show_manga(message):
    cid = message.chat.id
    if len(message.text.split(' ')) > 1:
        print('Haciendo Solicitud a la api')
        referral_all = message.text.split(" ")
        manga_name = " ".join(referral_all[1:])
        manga = search_manga(manga_name)
        if 'errors' in manga:
            reaction = ReactionTypeEmoji(type="emoji", emoji="🤷‍♀")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])

            for error in manga['errors']:
                match error['message']:
                    case "Not Found.":
                        bot.send_message(message.chat.id, f"Manga no encontrado 😣")
                    case _:
                        bot.send_message(message.chat.id, error['message'])
        else:
            reaction = ReactionTypeEmoji(type="emoji", emoji="⚡")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)

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
            tr_description = re.sub(html_regex, '', manga['data']['Media']['description'])
            description = GoogleTranslator(source=source_language, target=target_language).translate(tr_description)

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