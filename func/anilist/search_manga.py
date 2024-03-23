from database.mongodb import get_db
from func.api_anilist import search_manga, search_manga_id
from deep_translator import GoogleTranslator
from telebot.types import ReactionTypeEmoji, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
import requests
import re
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
db = get_db()
users = db.users

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


def search_mangas(message):
    if len(message.text.split(' ')) <= 1:
        bot.reply_to(message, f"Debes poner el nombre del manga luego de /manga")
        return
    
    print('Haciendo Solicitud a la api')
    referral_all = message.text.split(" ")
    anime_name = " ".join(referral_all[1:])
    anime = search_manga(anime_name)
     
    markup = InlineKeyboardMarkup(row_width=1)
    btns = []
    for res in anime['data']['Page']['media'][:min(len(anime['data']['Page']['media']), 8)]:
        if res['title']['english'] is not None:
            title = res['title']['english']
        else:
            title = res['title']['romaji']

        btn = InlineKeyboardButton(str(title), callback_data=f"show_manga_{res['id']}")
        btns.append(btn)
    markup.add(*btns)

    bot.reply_to(message, 'Estos son los resultados de la busqueda de mangas:', reply_markup=markup)


def show_manga(chat_id, message_id, id):
        manga = search_manga_id(id)
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

        if manga['data']['Media']['bannerImage'] is not None:
            image = manga['data']['Media']['bannerImage']
        else:
            image = manga['data']['Media']['coverImage']['large']
             
        msg = f"""
<strong>{name}</strong> 
<code>{', '.join(genres)}</code>
<strong>Descripción:</strong>
{description}

<strong>Estado:</strong> {status}
<strong>Para Adultos?:</strong> {adult}
"""

        if image is not None:
            link_preview_options = LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True)
        else:
            link_preview_options = LinkPreviewOptions(is_disabled=True)

        bot.edit_message_text(msg, chat_id, message_id, parse_mode="html", link_preview_options=link_preview_options)