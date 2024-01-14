import telebot
import requests
import json
import os

import PIL.Image

from dotenv import load_dotenv
from pymongo import MongoClient
from telebot.types import ReactionTypeEmoji

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users
Admins = db.admins

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


def reverse(message):
    chat_id = message.chat.id
    
    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        bot.reply_to(message, "Este comando es exclusivo de Otaku Senpai.")
        return
    
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.send_message(message.chat.id, f"Debes hacer reply a una imagen para poder describirla")
        return

    url = "https://saucenao.com/search.php"
    params = {
        "api_key": "ec9eb845f8d33c918976c7c03fbe5081867ed947",
        "output_type": "2",
        "testmode": "1"
    }

    fileID = message.reply_to_message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
        
    with open('image.jpg', 'rb') as img:
        # La imagen se proporciona en el parámetro 'files'
        response = requests.post(url, params=params, files={'file': img})

    res = json.loads(response.text)

    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])

    print(f"Haciendo soliticud a SauceNAO... user: @{message.from_user.username}")

    if 'results' in res:
        characters = None
        source = None
        for result in res['results']:
            if 'characters' in result['data']:
                characters = result['data']['characters']
            if 'source' in result['data'] and source is None:
                source = result['data']['source']
            if characters is not None and source is not None:
                break
            
        if characters is not None:
            text = f"**Búsqueda: {characters}**\n**Fuente: {source}**"
            bot.reply_to(message, "No se encontraron personajes en la respuesta de la API.")
            reaction = ReactionTypeEmoji(type="emoji", emoji="⚡")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
            bot.reply_to(message, text, parse_mode="Markdown")
        else:
            msg = bot.reply_to(message, "No se encontraron personajes en la respuesta de la API.")
            reaction = ReactionTypeEmoji(type="emoji", emoji="💅")
            bot.set_message_reaction(msg.chat.id, msg.message_id, reaction=[reaction])
    else:
        msg = bot.reply_to(message, "No se encontraron resultados en la API.")
        reaction = ReactionTypeEmoji(type="emoji", emoji="💅")
        bot.set_message_reaction(msg.chat.id, msg.message_id, reaction=[reaction])
