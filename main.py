import os
import re
import telebot
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from func.api_anilist import search_anime, search_manga
load_dotenv()



# Conectarse a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client.otakusenpai

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "I'm Alive!!!")
    print(message.from_user.username)


@bot.message_handler(regexp="Hola")
def say_hello(message):
    bot.send_message(message.chat.id, "Holiiii")
    print(message.from_user.username)



@bot.message_handler(commands=['anime'])
def anime(message):
    cid = message.chat.id
    if len(message.text.split('/anime ')) > 1:
        referral_all = message.text.split(" ")
        anime_name = " ".join(referral_all[1:])
        anime = search_anime(anime_name)

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
def anime(message):
    cid = message.chat.id
    if len(message.text.split('/manga ')) > 1:
        referral_all = message.text.split(" ")
        anime_name = " ".join(referral_all[1:])
        anime = search_manga(anime_name)

        name = anime['data']['Media']['title']['english']
        if (name is None):
            name = anime['data']['Media']['title']['romaji']

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
        description = re.sub(html_regex, '', anime['data']['Media']['description'])

        image = anime['data']['Media']['coverImage']['large']
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

    
if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "..."),
        telebot.types.BotCommand("/anime", "Buscar información sobre un anime"),
        telebot.types.BotCommand("/manga", "Buscar información sobre un manga")
    ])
    print('Iniciando el Bot')
    bot.infinity_polling()