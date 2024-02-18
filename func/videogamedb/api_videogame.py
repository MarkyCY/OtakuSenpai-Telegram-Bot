import requests
import json
import os
import re

from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from deep_translator import GoogleTranslator

load_dotenv()

VG_API = os.getenv('VIDEOG_DB')
#https://api.rawg.io/api/games?key=44ff5b65b2134929b8a321b6dde2bc34&search=silksong

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

def search_game(bot, message):
    if len(message.text.split(' ')) <= 1:
        bot.reply_to(message, f"Debes poner el nombre del videojuego luego de /game")
        return
    
    get_name = message.text.split(" ")
    name = " ".join(get_name[1:])
    
    print("Buscando Games")
    params = {
        "key": VG_API,
        "search": name
    }

    response = requests.get("https://api.rawg.io/api/games", params=params)
    res_json = json.loads(response.text)

    markup = InlineKeyboardMarkup(row_width=2)
    btns = []

    for res in res_json['results'][:min(len(res_json['results']), 5)]:
        btn = InlineKeyboardButton(res['name'], callback_data=f"videogame_{res['id']}")
        btns.append(btn)
    markup.add(*btns)


    bot.reply_to(message, 'Estos son los resultados de la busqueda de videojuegos:', reply_markup=markup)



def get_game(bot, chat_id, message_id, id):

    print("Buscando Game")
    
    params = {
        "key": VG_API
    }

    response = requests.get(f"https://api.rawg.io/api/games/{id}", params=params)
    res_json = json.loads(response.text)

    html_regex = re.compile(r'<[^>]+>')
    tr_description = re.sub(html_regex, '', res_json['description_raw'])[:500]
    description = GoogleTranslator(source=source_language, target=target_language).translate(tr_description)

    platforms = []
    for data in res_json['platforms']:
        platform = f"<code>{data['platform']['name']}</code>"
        platforms.append(platform)

    developers = []
    for data in res_json['developers']:
        developer = f"<code>{data['name']}</code>"
        developers.append(developer)

    tags = []
    for data in res_json['tags'][:min(len(res_json['tags']), 7)]:
        tag = f"<code>{data['name']}</code>"
        tags.append(tag)

    msg = f"""
<strong>{res_json['name']}</strong> 
{', '.join(platforms)}

<strong>Desarrolladores:</strong> {', '.join(developers)}

<strong>Descripción:</strong>
{description}

<strong>Lanzado:</strong> {res_json['released']}
<strong>Etiquetas:</strong> {', '.join(tags)}
"""
    if res_json['background_image'] is not None:
        link_preview_options = LinkPreviewOptions(url=res_json['background_image'], prefer_small_media=True)
    else:
        link_preview_options = LinkPreviewOptions(is_disabled=True)

    bot.edit_message_text(msg, chat_id, message_id, parse_mode="html", link_preview_options=link_preview_options)