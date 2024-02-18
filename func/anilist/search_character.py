from pymongo import MongoClient
from func.api_anilist import searchCharacter, searchCharacterId
from deep_translator import GoogleTranslator
from html2text import html2text
from telebot.types import ReactionTypeEmoji, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
import telebot
import requests
import re
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


def search_characters(message):
    if len(message.text.split(' ')) <= 1:
        bot.reply_to(message, f"Debes poner el nombre del personaje luego de /character")
        return
    
    print('Haciendo Solicitud a la api')
    referral_all = message.text.split(" ")
    character_name = " ".join(referral_all[1:])
    character = searchCharacter(character_name)
     
    markup = InlineKeyboardMarkup(row_width=1)
    btns = []
    for res in character['data']['Page']['characters'][:min(len(character['data']['Page']['characters']), 8)]:
        if res['name']['full'] is not None:
            name = res['name']['full']
        else:
            name = res['name']['native']

        btn = InlineKeyboardButton(str(name), callback_data=f"show_character_{res['id']}")
        btns.append(btn)
    markup.add(*btns)

    bot.reply_to(message, 'Estos son los resultados de la busqueda de personajes:', reply_markup=markup)


def show_character(chat_id, message_id, id):
        character = searchCharacterId(id)
         
        full_name = character['data']['Character']['name']['full']
        native_name = character['data']['Character']['name']['native']
        image = character['data']['Character']['image']['large']
        description_notr = character['data']['Character']['description'][:500]
        description_plain_text = html2text(description_notr)
        description_no_tag = re.sub('<[^<]*', '', description_plain_text)
        description = GoogleTranslator(source=source_language, target=target_language).translate(description_no_tag)
        gender = character['data']['Character']['gender']
        date_of_birth = character['data']['Character']['dateOfBirth']
        age = character['data']['Character']['age']
        blood_type = character['data']['Character']['bloodType']
        is_favorite = character['data']['Character']['isFavourite']
        site_url = character['data']['Character']['siteUrl']
         
        msg = f"""
<strong>{full_name}</strong> ({native_name})
<strong>Género:</strong> {gender}
<strong>Fecha de Nacimiento:</strong> {date_of_birth['year']}-{date_of_birth['month']}-{date_of_birth['day']}
<strong>Edad:</strong> {age}
<strong>Tipo de Sangre:</strong> {blood_type}
<strong>Favorito:</strong> {'Sí' if is_favorite else 'No'}
<strong>Enlace:</strong> {site_url}

<strong>Descripción:</strong>
{description}
"""
                 
        if image is not None:
            link_preview_options = LinkPreviewOptions(url=image, prefer_large_media=True, show_above_text=True)
        else:
            link_preview_options = LinkPreviewOptions(is_disabled=True)

        bot.edit_message_text(msg, chat_id, message_id, parse_mode="html", link_preview_options=link_preview_options)