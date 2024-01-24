from pymongo import MongoClient
from func.api_anilist import searchCharacter
from deep_translator import GoogleTranslator
from html2text import html2text
from telebot.types import ReactionTypeEmoji
import telebot
import requests
import re
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

source_language = 'auto'  # Auto detectar idioma de origen
target_language = 'es'  # español

def show_character(message):
    cid = message.chat.id
    if len(message.text.split(' ')) > 1:
        print('Haciendo Solicitud a la API')
        referral_all = message.text.split(" ")
        character_name = " ".join(referral_all[1:])
        character = searchCharacter(character_name)
        if 'errors' in character:
            reaction = ReactionTypeEmoji(type="emoji", emoji="🤷‍♀")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])

            for error in character['errors']:
                match error['message']:
                    case "Not Found.":
                        bot.reply_to(message, f"Personaje no encontrado 🙁")
                    case _:
                        bot.reply_to(message, error['message'])
        else:
            reaction = ReactionTypeEmoji(type="emoji", emoji="⚡")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)

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
            print(image)
            res = requests.get(image)
            with open("./file/" + full_name + ".jpg", 'wb') as out:
                out.write(res.content)
            foto = open("./file/" + full_name + ".jpg", "rb")

            #bot.send_message(cid, msg, parse_mode="html")
            bot.send_photo(cid, foto, msg, parse_mode="html", reply_to_message_id=message.message_id)
    else:
        bot.reply_to(message, f"Debes poner el nombre del personaje luego de /character")