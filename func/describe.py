import google.generativeai as genai
import telebot
import os
import PIL.Image
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users
Admins = db.admins

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

model = genai.GenerativeModel('gemini-pro-vision')

def describe(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(chat_id, message.from_user.id)

    if chat_id != -1001485529816:
        bot.reply_to(message, "Este comando es exclusivo de Otaku Senpai.")
        return

    if chat_member.status not in ['administrator', 'creator'] and not any(admin['user_id'] == user_id for admin in Admins.find()):
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return
    
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.send_message(message.chat.id, f"Debes hacer reply a una imagen para poder describirla")
        return
    
    try:
        fileID = message.reply_to_message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)

        with PIL.Image.open('image.jpg') as img:
            response = model.generate_content(["Describe la imagen y su procedencia si es posible, todo en español.", img])
            bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")