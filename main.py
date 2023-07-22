import os
import re
import random
import telebot
from pymongo import MongoClient
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException
#Horarios
import threading
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
#Triggers
from func.triggers.trigg import mostrar_pagina
from func.callback_query import callback_query
#Other Command
from func.bot_welcome import send_welcome
from func.info import info
from func.sticker_info import sticker_info
from func.list_admins import list_admins
from func.report import report
#Admin Command
from func.admin.warn import warn_user
from func.admin.ban import ban_user
from func.admin.unban import unban_user
from func.admin.unmute import unmute_user
from func.admin.mute import mute_user
#Api Anilist Use
from func.anilist.search_manga import show_manga
from func.anilist.search_anime import show_anime
#Concurso
from func.concurso.sub_user import subscribe_user
load_dotenv()



#Conectarse a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client.otakusenpai
contest = db.contest
Triggers = db.triggers

#VARIABLES DE ENTORNO .ENV
Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)

@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones_inline(call):
    callback_query(call)


@bot.message_handler(commands=['sticker_info'])
def send_sticker_info(message):
    sticker_info(message)

# Definimos una función que será llamada cuando ocurra un cambio en los miembros del grupo
@bot.message_handler(content_types=['new_chat_members'])
def on_chat_member_updated(message):
    # Verificamos si el objeto JSON contiene la clave "new_chat_members"
    if 'new_chat_members' in message.json:
        # Si el cambio es una nueva persona que se unió al grupo, llamamos a la función "send_welcome"
        send_welcome(message)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hola para subscribirte en el concurso solo escribe o toca: /sub")
    print(message.from_user.username)


@bot.message_handler(commands=['info'])
def command_info(message):
    info(message)
    

@bot.message_handler(commands=['anime'])
def anime(message):
    show_anime(message)


@bot.message_handler(commands=['manga'])
def manga(message):
    show_manga(message)


@bot.message_handler(commands=['sub'])
def command_to_subscribe(message):
    subscribe_user(message)


@bot.message_handler(commands=['list_admins'])
def command_list_admins(message):
    list_admins(message)
    

@bot.message_handler(commands=['report'])
def command_report(message):
    report(message)

#Triggers
@bot.message_handler(commands=['triggers'])
def command_triggers(message):
    resul = Triggers.find()
    trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
    for doc in resul:
        trigger_list.append(doc) # Agregamos cada documento a la lista

    #bot.send_message(message.chat.id, texto, parse_mode="html")
    mostrar_pagina(trigger_list, message.chat.id, message.from_user.id)

#End Triggers
    
@bot.message_handler(commands=['ban'])
def start_ban_user(message):
    try:
        ban_user(message)
    except ApiTelegramException as err:
        print(err)
        bot.send_message(message.from_user.id, f"Hola, mira esta es la razón por la que no se pudo ejecutar bien el comando: {err.description}")
        bot.reply_to(message, f"No se pudo ejecutar esta acción.")
    

@bot.message_handler(commands=['unban'])
def start_unban_user(message):
    try:
        unban_user(message)
    except ApiTelegramException as err:
        print(err)
        bot.send_message(message.from_user.id, f"Hola, mira esta es la razón por la que no se pudo ejecutar bien el comando: {err.description}")
        bot.reply_to(message, f"No se pudo ejecutar esta acción.")


@bot.message_handler(commands=['warn'])
def command_warn_user(message):
    try:
        warn_user(message)
    except ApiTelegramException as err:
        print(err)
        bot.send_message(message.from_user.id, f"Hola, mira esta es la razón por la que no se pudo ejecutar bien el comando: {err.description}")
        bot.reply_to(message, f"No se pudo ejecutar esta acción.")


@bot.message_handler(commands=['mute'])
def command_mute_user(message):
    try:
        mute_user(message)
    except ApiTelegramException as err:
        print(err)
        bot.send_message(message.from_user.id, f"Hola, mira esta es la razón por la que no se pudo ejecutar bien el comando: {err.description}")
        bot.reply_to(message, f"No se pudo ejecutar esta acción.")


@bot.message_handler(commands=['unmute'])
def command_unmute_user(message):
    try:
        unmute_user(message)
    except ApiTelegramException as err:
        print(err)
        bot.send_message(message.from_user.id, f"Hola, mira esta es la razón por la que no se pudo ejecutar bien el comando: {err.description}")
        bot.reply_to(message, f"No se pudo ejecutar esta acción.")

#Base de datos de prueba
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Check if the message is from a group or a supergroup
    if message.chat.type in ['group', 'supergroup']:
        # Get all the triggers and their corresponding responses from the database
        triggers = {}
        for doc in Triggers.find():
            triggers[doc["triggers"]] = doc["list_text"]
        # Create a regular expression pattern from the triggers
        pattern = re.compile("|".join(triggers.keys()))
        # Get the trigger from the message text
        match = pattern.search(message.text)
        if match:
            trigger = match.group()
            # Get a random response for the trigger from the database
            response = random.choice(triggers[trigger])
            # Send the response to the group or supergroup
            bot.reply_to(message, response)


# Define una lista para almacenar los datos de los usuarios que están en el flujo de conversación
users_in_flow = []

def scheduled_task():
    user_lst = []
    for user in contest.find({'contest_num': 1}):
                for sub in user['subscription']:
                    user_lst.append(sub['user'])

    for user_id in user_lst:
        bot.send_message(user_id, "Bien tienes 1 minuto para hallar la palabra magica y poderosa que @MarkyWTF ha seleccionado si lo conoces puede que la encuentres")

    time.sleep(10)

    for user_id in user_lst:
        msg = bot.send_message(user_id, "Listo, escribe la palabra mágica:")
        # Registrar la siguiente función para manejar la respuesta
        timer = threading.Timer(60.0, timeout_handler, args=[user_id])
        timer.start()
        users_in_flow.append({'user_id': user_id, 'timer': timer})
        bot.register_next_step_handler(msg, prueba)

def prueba(message):
    if message.text is not None:
        if message.text.lower() == "calvo":
            msg = bot.send_message(message.from_user.id, "No ya no es esa...")
            bot.register_next_step_handler(msg, prueba)
        elif message.text.lower() != "mamawebo":
            res = ["Jajaja no te acerques ni calentando", "Nooo, pero qué mal estás!", "¿Eso fue lo mejor que pudiste pensar?", "¡Ay, qué desastre!", "No, ni cerca. ¿En serio lo intentaste?", "¿Esa respuesta en serio?", "Jajaja, no te acerques ni por asomo.", "Esa respuesta es peor que el silencio.", "Qué lástima, esperaba más de ti.", "No, no, no. ¿Necesitas ayuda?", "¿Esa respuesta fue en serio o me estás troleando?", "¡No, no, no! ¿Dónde dejaste el cerebro?", "Si esa es tu mejor respuesta, mejor ni lo intentes."]
            response = random.choice(res)
            msg = bot.send_message(message.from_user.id, response)
            bot.register_next_step_handler(msg, prueba)
        else:
            bot.send_message(message.from_user.id, f'Waaa has respondido bieeen!!! Le avisaré a todos')
            clear_flow_by_user_id(message.chat.id)
            for user in contest.find({'contest_num': 1}):
                for sub in user['subscription']:
                    bot.send_message(sub['user'], f'Eeeey @{message.from_user.username} ha respondido bieeeen!')
    else:
        bot.send_message(message.from_user.id, "Necesito Texto Textoooooo!!!")

def timeout_handler(user_id):
    # Enviar un mensaje de tiempo agotado y cancelar el flujo de conversación para este usuario
    bot.send_message(user_id, 'Lo siento, se ha agotado el tiempo. Vuelve a intentarlo.')
    clear_flow_by_user_id(user_id)

def clear_timer_by_user_id(user_id):
    # Buscar el temporizador correspondiente al usuario y cancelarlo
    for user_data in users_in_flow:
        if user_data['user_id'] == user_id:
            user_data['timer'].cancel()
            users_in_flow.remove(user_data)
            break

def clear_flow_by_user_id(user_id):
    # Cancelar el flujo de conversación para el usuario y limpiar su temporizador
    bot.clear_step_handler_by_chat_id(user_id)
    clear_timer_by_user_id(user_id)

# Obtener la lista de usuarios desde la base de datos o desde otro lugar

# Crea una instancia de BackgroundScheduler
scheduler = BackgroundScheduler()
# Obtiene una instancia de pytz para la zona horaria deseada
tz = pytz.timezone('Cuba')
# Programa la tarea para que se ejecute cada hora CronTrigger(hour=22, minute=34, timezone=tz)
scheduler.add_job(scheduled_task, CronTrigger(hour=21, minute=44, timezone=tz))

# Inicia el scheduler
scheduler.start()

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "..."),
        telebot.types.BotCommand("/anime", "Buscar información sobre un anime"),
        telebot.types.BotCommand("/manga", "Buscar información sobre un manga"),
        telebot.types.BotCommand("/info", "Ver la información de un usuario"),
        telebot.types.BotCommand("/ban", "Banear a un Usuario"),
        telebot.types.BotCommand("/unban", "Desbanear a un Usuario"),
        telebot.types.BotCommand("/warn", "Advertencia para un usuario"),
        telebot.types.BotCommand("/mute", "Mutear a un Usuario"),
        telebot.types.BotCommand("/unmute", "Desmutear a un Usuario"),
        telebot.types.BotCommand("/sub", "Subscribirse al concurso")
    ])
    print('Iniciando el Bot')
    bot.infinity_polling()