from pymongo import MongoClient
from func.api_anilist import search_anime, search_anime_id
from deep_translator import GoogleTranslator
from telebot.types import ReactionTypeEmoji, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
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

def search_animes(message):
    if len(message.text.split(' ')) <= 1:
        bot.reply_to(message, f"Debes poner el nombre del anime luego de /anime")
        return
    
    print('Haciendo Solicitud a la api')
    referral_all = message.text.split(" ")
    anime_name = " ".join(referral_all[1:])
    anime = search_anime(anime_name)
     
    markup = InlineKeyboardMarkup(row_width=1)
    btns = []
    for res in anime['data']['Page']['media'][:min(len(anime['data']['Page']['media']), 8)]:
        if res['title']['english'] is not None:
            title = res['title']['english']
        else:
            title = res['title']['romaji']

        btn = InlineKeyboardButton(str(title), callback_data=f"show_anime_{res['id']}")
        btns.append(btn)
    markup.add(*btns)

    bot.reply_to(message, 'Estos son los resultados de la busqueda de animes:', reply_markup=markup)


def show_anime(chat_id, message_id, id):
    anime = search_anime_id(id)
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

    if anime['data']['Media']['bannerImage'] is not None:
        image = anime['data']['Media']['bannerImage']
    else:
        image = anime['data']['Media']['coverImage']['large']
     
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
     
    if image is not None:
        link_preview_options = LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True)
    else:
        link_preview_options = LinkPreviewOptions(is_disabled=True)
         
    bot.edit_message_text(msg, chat_id, message_id, parse_mode="html", link_preview_options=link_preview_options)