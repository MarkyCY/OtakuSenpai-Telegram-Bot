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
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
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
                        bot.reply_to(message, f"Manga no encontrado 😣")
                    case _:
                        bot.reply_to(message, error['message'])
        else:
            reaction = ReactionTypeEmoji(type="emoji", emoji="⚡")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)

            name = manga['data']['Media']['title']['english']
            if (name is None):
                name = manga['data']['Media']['title']['romaji']

            status = manga['data']['Media']['status']
            isAdult = manga['data']['Media']['isAdult']
            genres = manga['data']['Media']['genres']
            match isAdult:
                case True:
                    adult = "Si"
                case False:
                    adult = "No"
                case _:
                    adult = "Desconocido"

            html_regex = re.compile(r'<[^>]+>')
            if manga['data']['Media']['description'] is not None:
                tr_description = re.sub(html_regex, '', manga['data']['Media']['description'])
            else:
                tr_description = "No description."
            description = GoogleTranslator(source=source_language, target=target_language).translate(tr_description)

            image = manga['data']['Media']['coverImage']['large']
            res = requests.get(image)
            print(res.status_code, cid)
            with open("./file/" + name[:10] + ".jpg", 'wb') as out:
                out.write(res.content)
            foto = open("./file/" + name[:10] + ".jpg", "rb")

            msg = f"""
<strong>{name}</strong> 
<code>{', '.join(genres)}</code>
<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}
"""
        
            bot.send_photo(cid, foto, msg, parse_mode="html", reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, f"Debes poner el nombre del manga luego de /manga")