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

#Other Command
from func.bot_welcome import send_welcome
from func.sticker_info import sticker_info
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

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)


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
def info(message):
    #Verificar si el mensaje es una respuesta a otro mensaje
    if message.reply_to_message is not None:
        #Si el mensaje es un reply a otro mensaje, obtengo los datos del usuario al que se le hizo reply
        user = message.reply_to_message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        #Envio la información del usuario y su rol en un mensaje de reply al mensaje original
        bot.reply_to(message.reply_to_message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}")
    else:
        #Si el mensaje no es una respuesta a otro mensaje, obtener los datos del usuario que envió el comando
        user = message.from_user
        #Obtengo el rol del usuario en el chat
        chat_member = bot.get_chat_member(message.chat.id, user.id)
        role = chat_member.status
        bot.reply_to(message, f"ID: {user.id}\nNombre: {user.first_name}\nNombre de usuario: @{user.username}\nRol: {role.capitalize()}")


@bot.message_handler(commands=['anime'])
def anime(message):
    show_anime(message)


@bot.message_handler(commands=['manga'])
def manga(message):
    show_manga(message)


@bot.message_handler(commands=['sub'])
def command_to_subscribe(message):
    subscribe_user(message)

    
@bot.message_handler(commands=['ban'])
def start_ban_user(message):
    ban_user(message)


@bot.message_handler(commands=['list_admins'])
def list_admins(message):
    # obtén la información del chat
    chat_id = message.chat.id
    chat_info = bot.get_chat(chat_id)
    # obtén la lista de administradores del chat
    admins = bot.get_chat_administrators(chat_id)
    # crea una lista vacía para los nombres de los administradores (ignorando los bots)
    admin_names = []
    # itera sobre la lista de administradores y agrega los nombres de los que no son bots a la lista
    for admin in admins:
        if not admin.user.is_bot:
            admin_names.append(admin.user)
    # envía un mensaje con la lista de administradores al chat
    bot.send_message(chat_id, f"Los administradores de {chat_info.title} son:\n" + "\n".join([f'<a href="https://t.me/{user.username}">{user.first_name}</a>' for user in admin_names]), parse_mode='html', disable_web_page_preview=True)
    

@bot.message_handler(commands=['unban'])
def start_unban_user(message):
    unban_user(message)


@bot.message_handler(commands=['warn'])
def command_warn_user(message):
    warn_user(message)


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
    unmute_user(message)

#Base de datos de prueba
db = {
    "te quiero, aki": ["Yo te quiero maaas!", "Yo te Amooooo", "Wiiiiii"],
    "akira, despierta": ["Ahhh!! Aquí estoy", "Ya!! Estoy despiertaaa!", "Wenaaaaas que hora es?"],
    "a trabajar": ["Vamoooooos", "Aye Sir!!", "Shi"]
}
#Creo las expresiones regulares a partir de los datos de la base de datos
pattern = re.compile("|".join(db.keys()))

@bot.message_handler(func=lambda message: pattern.search(message.text))
def triggers(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        #Esta función devuelve los triggers asignados en la base de datos con las respuestas aleatorias que sean es puro entretenimiento la base de datos usada es solo de prueba
        match = pattern.search(message.text)
        if match:
            trigger = match.group()
            response = random.choice(db[trigger])
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