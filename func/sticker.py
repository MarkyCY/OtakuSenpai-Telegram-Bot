import telebot
import os

from dotenv import load_dotenv
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)



def sticker_info(message):
    chat_id = message.chat.id

    # Si el mensaje tiene un reply y es un sticker
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker_id = message.reply_to_message.sticker.file_id
        bot.send_message(chat_id, f"El ID del sticker es: <code>{sticker_id}</code>", reply_to_message_id=message.reply_to_message.message_id, parse_mode="html")

    # Si el mensaje tiene un reply pero no es un sticker
    elif message.reply_to_message and not message.reply_to_message.sticker:
        bot.send_message(chat_id, "Este comando solo puede ser usado con stickers. Por favor, haz reply a un sticker.", reply_to_message_id=message.reply_to_message.message_id)

    # Si el mensaje no tiene un reply
    else:
        bot.send_message(chat_id, "Por favor, haz reply a un sticker para obtener su ID.")