import os
import re
import telebot
import datetime
import google.generativeai as genai

from flask import Flask, request
from pyngrok import ngrok, conf
from waitress import serve

from database.mongodb import get_db
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException
#Horarios
import threading
import time

from telebot.types import ReactionTypeEmoji

#Personal Trigger
from func.inline.globales import respuesta_botones_inline
#Personal Trigger
from func.personal_triggers import *
#Blacklist
from func.blacklist.blacklist import *
#Other Command
from func.bot_welcome import send_welcome
from func.info import info
from func.sticker import sticker_info, steal_sticker, sticker_del
from func.list_admins import list_admins, isAdmin
from func.report import report
from func.describe import describe
from func.traduction import translate_command
from func.akira_ai import get_permissions_ai, akira_ai
from func.reverse import reverse
from func.afk import set_afk, get_afk
from func.set_bio import set_description
from func.useControl import useControlMongo
#VideoGames
from func.videogamedb.api_videogame import search_game
#Anime and manga gestion
from func.anime import *
#Inline Query
from func.inline_query import query_text
#Admin Command
from func.admin.warn import warn_user
from func.admin.ban import ban_user
from func.admin.unban import unban_user
from func.admin.unmute import unmute_user
from func.admin.mute import mute_user
#Triggers and Black Word
from func.triggers import command_triggers
from func.black_word import *
#Api Anilist Use
from func.anilist.search_manga import search_mangas
from func.anilist.search_anime import search_animes
from func.anilist.search_character import search_characters
#Concurso
from func.concurso.sub_user import subscribe_user, unsubscribe_user
from func.concurso.contest import contest_photo, command_help
#Evento
from func.event import calvicia, contest_event
import json
load_dotenv()

web_server = Flask(__name__)

@web_server.route('/', methods=['POST'])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200

#Conectarse a la base de datos MongoDB
db = get_db()
contest = db.contest
Contest_Data = db.contest_data
Triggers = db.triggers
Blacklist = db.blacklist
Admins = db.admins
users = db.users
Gartic = db.gartic
Tasks = db.tasks

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')

#Token de Gemini y llamada de modelo.
genai.configure(api_key=os.getenv('GEMINI_API'))
model = genai.GenerativeModel('gemini-pro')


#Control de uso diario
useControlMongoInc = useControlMongo()

bot = telebot.TeleBot(Token)

#Inline Query
@bot.inline_handler(lambda query: len(query.query) > 0)
def catch_query(inline_query):
    query_text(inline_query)


@bot.callback_query_handler(func=lambda x: True)
def res_inline(call):
    respuesta_botones_inline(call, bot)


@bot.message_handler(commands=['sticker_info'])
def send_sticker_info(message):
    sticker_info(message)

@bot.message_handler(commands=['del_sticker'])
def del_sticker_command(message):
    sticker_del(message)

# Definimos una función que será llamada cuando ocurra un cambio en los miembros del grupo
@bot.message_handler(content_types=['new_chat_members'])
def on_chat_member_updated(message):
    # Verificamos si el objeto JSON contiene la clave "new_chat_members"
    if 'new_chat_members' in message.json:
        # Si el cambio es una nueva persona que se unió al grupo, llamamos a la función "send_welcome"
        send_welcome(message)


@bot.message_handler(commands=['start'])
def start(message):
    if (message.chat.type == 'private'):
        bot.send_message(message.chat.id, "Hola para subscribirte en el concurso solo escribe o toca: /sub")
    else:
        bot.send_message(message.chat.id, "Uhhh quieres participar? Contactame por PV y escribeme /sub \n@Akira_Senpai_bot")
    print(message.from_user.username)


@bot.message_handler(commands=['info'])
def command_info(message):
    info(message)
    

@bot.message_handler(commands=['game'])
def anime(message):
    search_game(bot, message)

@bot.message_handler(commands=['anime'])
def anime(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
    search_animes(message)


@bot.message_handler(commands=['manga'])
def manga(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
    search_mangas(message)

@bot.message_handler(commands=['character'])
def character(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
    search_characters(message)


@bot.message_handler(commands=['sub'])
def command_to_subscribe(message):
    now = datetime.datetime.now()
    objetive = datetime(now.year, 3, 1, 14, 00)
    
    if now >= objetive:
        bot.reply_to(message, "Suscripciones Cerradas.")
        return
    
    if message.chat.type == 'private':
        subscribe_user(message)

@bot.message_handler(commands=['unsub'])
def command_to_unsubscribe(message):
    if message.chat.type == 'private':
        unsubscribe_user(message)


@bot.message_handler(commands=['list_admins'])
def command_list_admins(message):
    list_admins(message)
    

@bot.message_handler(commands=['report'])
def command_report(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
    report(message)

@bot.message_handler(commands=['blacklist'])
def command_blackwords(message):
    blacklist(message)

#@bot.message_handler(commands=['add_poll'])
@bot.message_handler(content_types=['poll'])
def command_add_poll(message):
    if (message.chat.type == 'private'):
        # Función de recursividad para registrar la respuesta del usuario
        #cid = message.chat.id
        uid = message.from_user.id

        isadmin = isAdmin(uid)
        if isadmin is not None:
            poll_data = message.poll
            
            #Steaps
            msg = bot.send_message(uid, f"¿Quieres agregar el poll? (si/no)")
            bot.register_next_step_handler(msg, verify_add_poll, poll_data)
            
def verify_add_poll(message, poll_data, validate=False):
    if message.text.lower() == "si" or validate is True:

        options = poll_data.options
            
        options_with_numbers = '\n'.join([f"{i}. {option.text}" for i, option in enumerate(options)])

        msg = bot.send_message(message.from_user.id, f"Escribe el número de la respuesta correcta:\n\n{options_with_numbers}")
        bot.register_next_step_handler(msg, write_num, poll_data, options)
    elif message.text.lower() == "no":
        bot.send_message(message.from_user.id, "No se agregará el poll.")
    else:
        msg = bot.send_message(message.from_user.id, "Respuesta inválida. Por favor, responde con 'si' o 'no'.")
        bot.register_next_step_handler(msg, verify_add_poll, poll_data)

def write_num(message, poll_data, options):
        if message.text is not None:
            try:
                num = int(message.text)
            except ValueError:
                msg = bot.send_message(message.from_user.id, "Eso no es un número, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, verify_add_poll, poll_data, True)
                return
            
            if num > len(options):
                msg = bot.send_message(message.from_user.id, "Ese número no está entre las opciones, inténtalo de nuevo:")
                bot.register_next_step_handler(msg, verify_add_poll, poll_data, True)
            else:
                num = int(message.text)
                pass

        question = poll_data.question

        # Enviar la información al usuario
        response = f"Pregunta: {question}\nOpciones:{', '.join([option.text for option in options])}\nRespuesta Correcta: {options[num].text}"
        cooldown = 60

        bot.send_message(message.chat.id, response)
        time = "2023-11-24 12:02:00-05:00"
        data = {
            "question": question,
            "options": [option.text for option in options],
            "correct": num,
            "cooldown": cooldown,
            }
        try:
            msg = bot.send_message(message.from_user.id, f"Agrega una fecha especifica para la salida del poll:\nFormato: <code>{time}</code>\n\n<code>2023-11-24</code>: Esta parte representa la fecha en formato año-mes-día. En este caso, la fecha es el 24 de noviembre de 2023.\n\n<code>12:02:00</code>: Esta parte representa la hora en formato hora:minuto:segundo. En este caso, la hora es las 12:02:00.\n\n<code>-05:00</code>: Esta parte representa el desplazamiento horario en formato +/-HH:MM. En este caso, el desplazamiento horario es de -05:00, lo que indica que la hora está en la zona horaria GMT-5.\n⚠️Esta opción no debe ser modificada.", parse_mode="html")
            bot.register_next_step_handler(msg, endPollAdd, data)
        except ApiTelegramException as err:
            print(err)

def endPollAdd(message, data):
    pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}-\d{2}:\d{2}"
    if re.match(pattern, message.text):
        data["date"] = message.text
        json_data = json.dumps(data)
        print(json_data)
        Tasks.insert_one(json_data)
        bot.send_message(message.from_user.id, f"Se ha agregado la encuesta correctamente a la base de datos con la siguiente fecha:\n{data['date']}")
    else:
        msg = bot.send_message(message.from_user.id, f"Formato inválido, inténtalo de nuevo:")
        bot.register_next_step_handler(msg, endPollAdd, data)

    
@bot.message_handler(commands=['subs'])
def res_con_command(message):
    res = contest.find_one({'contest_num': 1})
    text = "Suscriptores:\n"
    for i, val in enumerate(res['subscription']):
        i = i + 1

        chat_member = bot.get_chat_member(-1001485529816, val['user'])
        if chat_member.user.username is not None:
            text += f"\n{i}- <a href='https://t.me/{chat_member.user.username}'>{chat_member.user.username}</a>" 
        else:
            text += f"\n{i}- <a href='tg://user?id={chat_member.user.id}'>{chat_member.user.first_name}</a>" 
    bot.reply_to(message, text, parse_mode="html", disable_web_page_preview=True)

@bot.message_handler(commands=['vsubs'])
def res_con_command(message):
    contest_event(message)

#@bot.message_handler(commands=['send_spm'])
#def send_msg_contest(message):
#    msg = """
#Hola mi amor, ya se que el concurso tuvo que terminar antes pero no se puede hacer nada es culpa de @YosvelPG.
#De todas formas te escribo para avisarte que mañana si cierra la inscripción del concurso y el sábado ya anuncio los ganadores.
#Si aún no has entregado apurese mi love que mire que horas son! Hay más premios además del saldo de 250 :D
#"""
#    res = contest.find_one({'contest_num': 1})
#    for val in res['subscription']:
#        id = val['user']
#        print(id)
#        try:
#            bot.send_message(id, msg, parse_mode="html")
#        except ApiTelegramException as e:
#            print(e)


@bot.message_handler(commands=['set_bio'])
def set_bio_command(message):
    set_description(message)

@bot.message_handler(commands=['afk'])
def afk_command(message):
    set_afk(message)

@bot.message_handler(func=lambda message: message.text.lower().startswith('brb') or message.text.lower().startswith('brb '))
def brb_command(message):
    set_afk(message)


@bot.message_handler(commands=['add_anime'])
def add_anime_command(message):
    add_anime(message)

@bot.message_handler(commands=['del_anime'])
def del_anime_command(message):
    del_anime(message)

@bot.message_handler(commands=['tr'])
def tr_command(message):
    translate_command(message)

@bot.message_handler(commands=['reverse'])
def reverse_command(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction], is_big=True)
    reverse(message)

@bot.message_handler(commands=['perm_ai'])
def akira_perm_ai(message):
    get_permissions_ai(message)

@bot.message_handler(commands=['steal'])
def steal_sticker_command(message):
    steal_sticker(message)
                    
@bot.message_handler(commands=['describe'])
def describe_command(message):
    reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
    describe(message)

@bot.message_handler(commands=['triggers'])
def call_triggers(message):
    command_triggers(message, bot)


@bot.message_handler(commands=['day'])
def handle_day_message(message):
    
    chat_id = message.chat.id
    parts = message.text.split()
    num = int(parts[1])

    now = datetime.datetime.now()

    # Añadir el número de minutos especificado
    new_time = now + datetime.timedelta(seconds=num)
    
    # Extraer la hora y los minutos de la nueva fecha y hora
    #hour = new_time.hour
    #minute = new_time.minute
    seconds = new_time.second
    bot.send_message(chat_id, f"Dentro de: {num} seg, te notifico. ")
    try:
        #scheduler.add_job(calvicia, CronTrigger(hour=hour, minute=minute, second=seconds, timezone=tz), args=(-1001664356911, num))
        timer = threading.Timer(num, calvicia, args=[chat_id, num])
        timer.start()
    except ApiTelegramException as err:
        print(err)


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


#scheduler.add_job(calvicia, CronTrigger(hour=hour, minute=minute, second=seconds, timezone=tz), args=(-1001664356911, num))

@bot.message_handler(content_types=['photo'])
def recive_photo_contest(message):
    contest_photo(message, bot)


@bot.message_handler(chat_types=['private']) # You can add more chat types
def recive_text_contest(message):
    command_help(message, bot)


#@bot.message_handler(commands=['start_play'])
#def gartic(message):
#    
#    caracteres_permitidos = string.ascii_uppercase + string.digits
#    codigo = ''.join(random.choice(caracteres_permitidos) for _ in range(5))
#    topic_id = message.message_thread_id
#    bot.reply_to(message, f"Va a empezar el juego toca el botón para unirte.")
#    markup = InlineKeyboardMarkup()
#    join = InlineKeyboardButton("🎨Unirse", callback_data=f"join_{codigo}")
#    markup.row(join)
#
#    bot.send_message(message.chat.id, f"Mira un código, que bonito! <code>/join {codigo}</code>\nYa hay un botón wiiiiii!", parse_mode="html", reply_markup=markup, message_thread_id=topic_id)
#
#    #bot.register_next_step_handler(message, cacioc)
#
#@bot.message_handler(commands=['join'])
#def gartic_join(message):
#    referral_all = message.text.split(" ")
#    code = str(referral_all[1])
#    print(code)
#
#def cacioc(message):
#    frases = {
#        'MarkyWTF': '1',
#        'Nivita3': '2'
#    }
#
#    jugadores = list(frases.keys())
#
#    frases_asignadas = {}
#    foto = open("./file/_blank.jpg", "rb")
#    print(foto)
#    
#    while jugadores:
#        jugador = jugadores.pop()
#        frases_disponibles = [frase for clave, frase in frases.items() if clave != jugador and frase not in frases_asignadas.values()]
#        frase_asignada = random.choice(frases_disponibles)
#        frases_asignadas[jugador] = frase_asignada
#        user = users.find_one({"username": jugador})
#        chat_id_origen = 873919300
#
#        # ID del mensaje a reenviar
#        mensaje_id = 1712
#
#        # Reenviar el mensaje
#        bot.forward_message(user["user_id"], chat_id_origen, mensaje_id)
#        #bot.send_photo(user["user_id"], foto, "edita esto pa ver si silve")
#
#    print(frases_asignadas)


#LAMBDA
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    #Leave Group
    group_perm = [-1001485529816, -1001664356911, -1001223004404]
    
    if message.chat.type in ['supergroup', 'group']:
        if message.chat.id not in group_perm:
            bot.send_message(message.chat.id, 'Lo siento solo puedo ser usada en <a href="https://t.me/OtakuSenpai2020">Otaku Senpai</a>', parse_mode="HTML")
            bot.leave_chat(message.chat.id)
            return
    
    if message.chat.type in ['group', 'supergroup']:
        black_word(bot, Blacklist, message)

        #trigger_word(bot, Triggers, message)
        
        akira_ai(message)

        get_afk(bot, message)
                

if __name__ == '__main__':
    ngrok_token = os.getenv('NGROK_TOKEN')

    bot.set_my_commands([
        telebot.types.BotCommand("/start", "..."),
        telebot.types.BotCommand("/anime", "Buscar información sobre un anime"),
        telebot.types.BotCommand("/manga", "Buscar información sobre un manga"),
        telebot.types.BotCommand("/game", "Buscar información sobre videojuegos"),
        telebot.types.BotCommand("/character", "Buscar información sobre un personaje"),
        telebot.types.BotCommand("/afk", "Modo afk"),
        telebot.types.BotCommand("/steal", "Obtener Stickers"),
        telebot.types.BotCommand("/del_sticker", "Eliminar Sticker del Pack"),
        telebot.types.BotCommand("/set_bio", "Poner descripción"),
        telebot.types.BotCommand("/info", "Ver la información de un usuario"),
        telebot.types.BotCommand("/tr", "Traducir elementos"),
        telebot.types.BotCommand("/triggers", "Gestión de los Triggers"),
        telebot.types.BotCommand("/perm_ai", "Permitir IA"),
        telebot.types.BotCommand("/describe", "Analizar imagen"),
        telebot.types.BotCommand("/reverse", "Buscar personaje"),
        telebot.types.BotCommand("/add_anime", "Agregar anime a la base de datos"),
        telebot.types.BotCommand("/del_anime", "Eliminar anime a la base de datos"),
        telebot.types.BotCommand("/blacklist", "Gestión de la lista negra"),
        telebot.types.BotCommand("/list_admins", "Listado de Administradores"),
        telebot.types.BotCommand("/ban", "Banear a un Usuario"),
        telebot.types.BotCommand("/unban", "Desbanear a un Usuario"),
        telebot.types.BotCommand("/warn", "Advertencia para un usuario"),
        telebot.types.BotCommand("/mute", "Mutear a un Usuario"),
        telebot.types.BotCommand("/unmute", "Desmutear a un Usuario"),
        telebot.types.BotCommand("/sub", "Subscribirse al concurso")
    ])
    #bot.remove_webhook()
    #time.sleep(1)
    #print('Iniciando el Bot')
    #bot.infinity_polling()
    conf.get_default().config_path = "./config_ngrok.yml"
    conf.get_default().region = "us"
    ngrok.set_auth_token(ngrok_token)
    ngrok_tunel = ngrok.connect(5000, bind_tls=True)
    ngrok_url = ngrok_tunel.public_url
    print("URL NGROK: ", ngrok_url)
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=ngrok_url)
    #web_server.run(host="0.0.0.0", port=5000)
    serve(web_server, host="0.0.0.0", port=5000)