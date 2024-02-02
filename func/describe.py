import google.generativeai as genai
import telebot
import os
import PIL.Image
from dotenv import load_dotenv
from pymongo import MongoClient
from func.useControl import useControlMongo
from telebot.types import ReactionTypeEmoji

load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
users = db.users
Admins = db.admins

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

useControlMongoInc = useControlMongo()

model = genai.GenerativeModel('gemini-pro-vision')

def describe(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_id != -1001485529816 and message.from_user.id != 873919300:
        bot.reply_to(message, "Este comando es exclusivo de Otaku Senpai.")
        return

    #if chat_member.status not in ['administrator', 'creator'] and not any(admin['user_id'] == user_id for admin in Admins.find()):
    #    bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    #    return

    #Verificar si no se ha llegado al limite de uso
    if useControlMongoInc.verif_limit(user_id) is False and not any(admin['user_id'] == user_id for admin in Admins.find()):
        msg = bot.reply_to(message, "Has llegado al límite de uso diario!")
        reaction = ReactionTypeEmoji(type="emoji", emoji="🥴")
        bot.set_message_reaction(message.chat.id, msg.message_id, reaction=[reaction])
        return

    
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.send_message(message.chat.id, f"Debes hacer reply a una imagen para poder describirla")
        return
    
    reaction = ReactionTypeEmoji(type="emoji", emoji="🤔")
    bot.set_message_reaction(message.chat.id, message.reply_to_message.message_id, reaction=[reaction])

    try:
        fileID = message.reply_to_message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)

        with PIL.Image.open('image.jpg') as img:
            response = model.generate_content(["Describe la imagen y su procedencia si es posible, y da tu opinión sobre ella, todo en español.", img])
            msg = bot.reply_to(message, response.text)
            
            reaction = ReactionTypeEmoji(type="emoji", emoji="🤓")
            bot.set_message_reaction(message.chat.id, msg.message_id, reaction=[reaction])
            #Registrar uso
            useControlMongoInc.reg_use(user_id)
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")