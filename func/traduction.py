import telebot
import os

from deep_translator import GoogleTranslator
from dotenv import load_dotenv
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def translate_command(message):
    # Obtener el texto después del comando /tr
    if message.reply_to_message:
        text_to_translate = message.reply_to_message.text[4:].strip()
    
        # Idiomas de origen y destino
        source_language = 'auto'  # Auto detectar idioma de origen
        target_language = 'es'  # español
    
        try:
            # Realizar la traducción
            translation = GoogleTranslator(source=source_language, target=target_language).translate(text_to_translate)
    
            # Enviar la traducción al usuario
            bot.reply_to(message, f"Traducción 'ES': {translation}")
    
        except Exception as e:
            # Manejar cualquier error durante la traducción
            bot.reply_to(message, f"Ocurrió un error durante la traducción: {str(e)}")