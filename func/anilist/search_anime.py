from pymongo import MongoClient
from func.api_anilist import search_anime
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

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def show_anime(message):
    cid = message.chat.id
    if len(message.text.split(' ')) > 1:
        print('Haciendo Solicitud a la api')
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