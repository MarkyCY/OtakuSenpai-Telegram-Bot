import telebot
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
users = db.users

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

def write_num(message, options):
        if message.text is not None:
            try:
                num = int(message.text)
            except ValueError:
                msg = bot.send_message(message.from_user.id, "Eso no es un número, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, write_num, options)
                return
            if num > len(options):
                msg = bot.send_message(message.from_user.id, "Ese número no está entre las opciones, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, write_num, options)
            else:
                num = int(message.text)
                # Registrar la respuesta del usuario
                #users.update_one({'user_id': uid}, {'$set': {'contest.0.answer': num}})
                bot.send_message(message.from_user.id, "¡Listo! Tu respuesta ha sido registrada.")
        
def addPoll(message):
    # Función de recursividad para registrar la respuesta del usuario
    cid = message.chat.id
    uid = message.from_user.id

    # Verificar si el mensaje es una respuesta y si es una encuesta
    if message.reply_to_message and message.reply_to_message.poll:
        poll_data = message.reply_to_message.poll
        question = poll_data.question
        options = poll_data.options

        # Buscar la respuesta correcta en las opciones
        correct_option_text = None
        for option in options:
            if option.voter_count == poll_data.correct_option_id:
                correct_option_text = option.text
                break

        if cid != uid:
            bot.reply_to(message, "Te escribí por Pv para que selecciones la respuesta correcta.")
            
        # Enviar la información al usuario
        options_with_numbers = '\n'.join([f"{i}. {option.text}" for i, option in enumerate(options)])
        response = f"Pregunta: {question}\nOpciones:{', '.join([option.text for option in options])}\nRespuesta Correcta: {correct_option_text}"
        bot.send_message(message.chat.id, response)
        #Steaps
        msg = bot.send_message(uid, f"Ahora, escribe el número de la respuesta correcta:\n\n{options_with_numbers}")
        bot.register_next_step_handler(msg, write_num, options)

    else:
        bot.reply_to(message, "Este comando solo funciona en respuesta a un mensaje de encuesta.")
