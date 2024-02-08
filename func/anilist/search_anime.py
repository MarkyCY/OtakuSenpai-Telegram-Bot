from pymongo import MongoClient
from func.api_anilist import search_anime
from deep_translator import GoogleTranslator
from telebot.types import ReactionTypeEmoji
import requests
from datetime import datetime
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

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

def timestamp_conv(timestamp):
    date = datetime.fromtimestamp(timestamp)
    format = date.strftime("%d/%m/%Y")
    return format

def show_anime(message):
    cid = message.chat.id
    if len(message.text.split(' ')) > 1:
        print('Haciendo Solicitud a la api')
        referral_all = message.text.split(" ")
        anime_name = " ".join(referral_all[1:])
        anime = search_anime(anime_name)
        if 'errors' in anime:
            reaction = ReactionTypeEmoji(type="emoji", emoji="🤷‍♀")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
            for error in anime['errors']:
                match error['message']:
                    case "Not Found.":
                        bot.reply_to(message, f"Anime no encontrado 🙁")
                    case _:
                        bot.reply_to(message, error['message'])
        else:
            reaction = ReactionTypeEmoji(type="emoji", emoji="⚡")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
            
            name = anime['data']['Media']['title']['english']
            if (name is None):
                name = anime['data']['Media']['title']['romaji']

            duration = anime['data']['Media']['duration']
            episodes = anime['data']['Media']['episodes']
            status = anime['data']['Media']['status']
            isAdult = anime['data']['Media']['isAdult']
            nextAiringEpisode = anime['data']['Media']['nextAiringEpisode']
            genres = anime['data']['Media']['genres']

            match isAdult:
                case True:
                    adult = "Si"
                case False:
                    adult = "No"
                case _:
                    adult = "Desconocido"

            html_regex = re.compile(r'<[^>]+>')
            tr_description = re.sub(html_regex, '', anime['data']['Media']['description'])[:500]
            description = GoogleTranslator(source=source_language, target=target_language).translate(tr_description)
            image = anime['data']['Media']['coverImage']['large']
            res = requests.get(image)
            print(res.status_code, cid)
            with open("./file/" + name + ".jpg", 'wb') as out:
                out.write(res.content)
            foto = open("./file/" + name + ".jpg", "rb")

            msg = f"""
<strong>{name}</strong> 
<code>{', '.join(genres)}</code>
<strong>Duración de cada Cap:</strong> {duration} min
<strong>Episodios:</strong> {episodes}

<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}
"""
            if nextAiringEpisode:
                msg += f"\n<strong>Próxima emisión:</strong>\nEpisodio <strong>{nextAiringEpisode['episode']}</strong> Emisión: <code>{timestamp_conv(nextAiringEpisode['airingAt'])}</code>\n"

            #bot.send_message(cid, msg, parse_mode="html")
            bot.send_photo(cid, foto, msg, parse_mode="html", reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, f"Debes poner el nombre del anime luego de /anime")