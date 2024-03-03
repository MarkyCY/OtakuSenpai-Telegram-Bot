import os
import re
import random
import telebot
import datetime
import google.generativeai as genai

from flask import Flask, request
from pyngrok import ngrok, conf
from waitress import serve

from pymongo import MongoClient
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException
#Horarios
import threading
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji, ReplyKeyboardMarkup, ReplyKeyboardRemove
import pickle
from bson import ObjectId

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
from func.afk import set_afk
from func.set_bio import set_description
from func.useControl import useControlMongo
#VideoGames
from func.videogamedb.api_videogame import search_game, get_game
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
#Api Anilist Use
from func.anilist.search_manga import show_manga, search_mangas
from func.anilist.search_anime import show_anime, search_animes
from func.anilist.search_character import show_character, search_characters
#Concurso
from func.concurso.sub_user import subscribe_user, unsubscribe_user, send_data_contest
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
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
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

#Cantidad de rows por página en paginación
ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))

JUECES = {938816655, 1881435398, 5602408597, 5825765407, 1221472021, 873919300, 5963355323}

#Control de uso diario
useControlMongoInc = useControlMongo()

bot = telebot.TeleBot(Token)

#Inline Query
@bot.inline_handler(lambda query: len(query.query) > 0)
def catch_query(inline_query):
    query_text(inline_query)


@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones_inline(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    uid = call.from_user.id

    #Search VideoGame
    def is_search_vg(variable):
            pattern = r"^videogame_(\d+)$"
            return bool(re.match(pattern, variable))
    
    def is_search_anime(variable):
            pattern = r"^show_anime_(\d+)$"
            return bool(re.match(pattern, variable))
    
    def is_search_manga(variable):
            pattern = r"^show_manga_(\d+)$"
            return bool(re.match(pattern, variable))
    
    def is_search_character(variable):
            pattern = r"^show_character_(\d+)$"
            return bool(re.match(pattern, variable))
    
    if is_search_vg(call.data):
        if not call.message.reply_to_message:
            bot.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
            bot.delete_message(cid, mid)
            return
        if call.message.reply_to_message.from_user.id != uid:
            bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
            return
        parts = call.data.split("_")
        get_game(bot, cid, mid, parts[1])
        return
    
    if is_search_anime(call.data):
        if not call.message.reply_to_message:
            bot.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
            bot.delete_message(cid, mid)
            return
        if call.message.reply_to_message.from_user.id != uid:
            bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
            return
        parts = call.data.split("_")
        show_anime(cid, mid, parts[2])
        return
    
    if is_search_manga(call.data):
        if not call.message.reply_to_message:
            bot.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
            bot.delete_message(cid, mid)
            return
        if call.message.reply_to_message.from_user.id != uid:
            bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
            return
        parts = call.data.split("_")
        show_manga(cid, mid, parts[2])
        return
    
    if is_search_character(call.data):
        if not call.message.reply_to_message:
            bot.answer_callback_query(call.id, "No se encontró el reply del mensaje.")
            bot.delete_message(cid, mid)
            return
        if call.message.reply_to_message.from_user.id != uid:
            bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
            return
        parts = call.data.split("_")
        show_character(cid, mid, parts[2])
        return


    #Contest
    emojis = {"1": "1️⃣","2": "2️⃣","3": "3️⃣","4": "4️⃣","5": "5️⃣","6": "6️⃣","7": "7️⃣","8": "8️⃣","9": "9️⃣","10": "🔟"}
    if uid in JUECES:

        def is_vote_contest(variable):
            pattern = r"^contest_vote_(10|[1-9])_\d{8,11}_(0|1)$"
            return bool(re.match(pattern, variable))

        # 0 => Photo, 1 => Text
        if is_vote_contest(call.data):
            partes = call.data.split("_")

            match partes[4]:
                case "0":
                    type = "photo"
                case "1":
                    type = "text"

            contest = Contest_Data.find_one({'u_id': int(partes[3]), 'type': type})
            if contest is None:
                bot.answer_callback_query(call.id, f"No existe este documento...")
                return
            
            if 'vote' in contest and str(uid) in contest['vote']:
                bot.answer_callback_query(call.id, f"Votado actualizado de: {contest['vote'][str(uid)]} a {partes[2]}")
            else:
                bot.answer_callback_query(call.id, f"Has Votado: {partes[2]}")

            if type == 'photo':
                msg = call.message.caption
            if type == 'text':
                msg = call.message.text

            name = call.from_user.first_name

            if re.search(r'(' + re.escape(name) + r'\d+️⃣|' + re.escape(name) + r'🔟)', msg):
                msg = re.sub(r'(' + re.escape(name) + r'\d+️⃣|' + re.escape(name) + r'🔟)', f'{name}{emojis[partes[2]]}', msg)
            else:
                msg += f'\n{name}{emojis[partes[2]]}'
            #msg = f"Foto de concurso:\nHas votado: {emojis[partes[2]]}"

            markup = InlineKeyboardMarkup(row_width=5)
            btns = []
            for i in range(1, 11):
                btn = InlineKeyboardButton(str(i), callback_data=f"contest_vote_{i}_{partes[3]}_{partes[4]}")
                btns.append(btn)
            markup.add(*btns)
            
            if type == 'photo':
                bot.edit_message_caption(msg, cid, mid, reply_markup=markup)
            if type == 'text':
                bot.edit_message_text(msg, cid, mid, reply_markup=markup)

            Contest_Data.update_one(
               {'u_id': int(partes[3]), 'type': type},
               { "$set": { "vote." + str(uid): int(partes[2]) } }
            )

            return
        #End contest
    
    chat_member = bot.get_chat_member(cid, uid)
    isadmin = isAdmin(uid)

    ADMIN_IDS = {1221472021, 5579842331, 5174301596}

    if chat_member.status not in ['administrator', 'creator'] and uid not in ADMIN_IDS and isadmin is None:
        bot.answer_callback_query(call.id, "Solo los administradores pueden usar este comando.")
        return
    
    datos = pickle.load(open(f'./data/{cid}_{mid}', 'rb'))

    #if u_name == "MarkyWTF":
    #    pass
    #else:
    #    if datos["user_id"] != uid:
    #        bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
    #        return

    if call.data == "close":
        bot.delete_message(cid, mid)
        os.remove(f'./data/{cid}_{mid}')
        return
    
    if call.data == "add":
        add_trigger(cid, uid, mid)
        return
    
    if call.data == "add_bw":
        add_blackword(cid, uid, mid)
        return

    if call.data == "back":
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(datos['lista'], cid, uid, datos["pag"], mid)
        return
    
    if call.data == "prev":
        if datos["pag"] == 0:
            bot.answer_callback_query(call.id, "Ya estás en la primera página")
        else:
            datos["pag"]-= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina(datos['lista'], cid, uid, datos["pag"], mid)
        return

    if call.data == "next":
        if datos["pag"] * ROW_X_PAGE + ROW_X_PAGE >= len(datos["lista"]):
            bot.answer_callback_query(call.id, "Ya estás en la ultima página")
        else:
            datos["pag"]+= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina(datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if call.data == "prev_bl":
        if datos["pag"] == 0:
            bot.answer_callback_query(call.id, "Ya estás en la primera página")
        else:
            datos["pag"]-= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina_bl(datos['lista'], cid, uid, datos["pag"], mid)
        return

    if call.data == "next_bl":
        if datos["pag"] * ROW_X_PAGE + ROW_X_PAGE >= len(datos["lista"]):
            bot.answer_callback_query(call.id, "Ya estás en la ultima página")
        else:
            datos["pag"]+= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina_bl(datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if ObjectId.is_valid(call.data):
        mostrar_triggers(call.data, cid, mid)
        return
    

    #Triggers and Blacklist
    def is_valid_blackword(variable):
        pattern = r"^bw_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    
    if is_valid_blackword(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        Blacklist.delete_one({"_id": ObjectId(o_id)})
        resul = Blacklist.find()
        blackword_list = []
        for doc in resul:
            blackword_list.append(doc)
        page = 0
        datos = {"pag":page, "lista":blackword_list, "user_id": uid}
        os.remove(f'./data/{cid}_{mid}')
        time.sleep(1)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina_bl(blackword_list, cid, uid, page, mid)
        msg = bot.send_message(cid, f"Palabra eliminada")
        time.sleep(5)
        bot.delete_message(cid, msg.message_id)
        return

    def is_valid_to_edit(variable):
        pattern = r"^[a-f\d]{24}_\d$"
        return bool(re.match(pattern, variable))
    def is_valid_edit(variable):
        pattern = r"^edit_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_valid_push_trigger(variable):
        pattern = r"^push_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_valid_edit_text(variable):
        pattern = r"^edit_[a-f\d]{24}_\d$"
        return bool(re.match(pattern, variable))
    def is_delete_text(variable):
        pattern = r"^del_[a-f\d]{24}_\d$"
        return bool(re.match(pattern, variable))
    def is_delete_trigger(variable):
        pattern = r"^del_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_gput_trigger(variable):
        pattern = r"^gput_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_gquit_trigger(variable):
        pattern = r"^gquit_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    
    if is_valid_to_edit(call.data):
        partes = call.data.split("_")
        o_id = partes[0]
        sel = partes[1]
        doc = Triggers.find_one({"_id": ObjectId(o_id)})

        menu_trigger(cid, uid, doc['_id'], sel)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(datos["lista"], cid, uid, datos["pag"], mid)
        return

    if is_delete_trigger(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        del_trigger(cid, mid, o_id, uid)
        return
    
    if is_valid_edit_text(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        sel = partes[2]
        os.remove(f'./data/{cid}_{mid}')
        bot.delete_message(cid, mid)
        edit_trigger_text(uid, uid, o_id, sel)
        return
    
    if is_valid_edit(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        edit_trigger(uid, uid, o_id, datos["pag"], mid)
        return
    
    if is_valid_push_trigger(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        add_trigger_text(uid, uid, o_id)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if is_delete_text(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        sel = partes[2]
        del_trigger_text(cid, mid, o_id, sel)
    
    if is_gput_trigger(call.data):
        print("haciendo global")
        partes = call.data.split("_")
        o_id = partes[1]
        Triggers.update_one({'_id': ObjectId(o_id)}, {"$set": {"eq": True}})
        resul = Triggers.find()
        trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
        for doc in resul:
            trigger_list.append(doc) # Agregamos cada documento a la lista
        mostrar_pagina(trigger_list, cid, uid, datos["pag"], mid)
        
    if is_gquit_trigger(call.data):
        print("quitando global")
        partes = call.data.split("_")
        o_id = partes[1]
        Triggers.update_one({'_id': ObjectId(o_id)}, {"$set": {"eq": False}})
        resul = Triggers.find()
        trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
        for doc in resul:
            trigger_list.append(doc) # Agregamos cada documento a la lista
        mostrar_pagina(trigger_list, cid, uid, datos["pag"], mid)





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

def add_blackword(cid, uid, msg_id):
    msg = bot.send_message(uid, f"Escribe la nueva palabra:")
    bot.register_next_step_handler(msg, catch_new_blackword, uid, msg_id, cid)

def catch_new_blackword(msg, uid, msg_id, cid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Blacklist.insert_one({ "blackword": msg.text })
            resul = Blacklist.find()
            blackword_list = []
            for doc in resul:
                blackword_list.append(doc)
            page = 0
            datos = {"pag":page, "lista":blackword_list, "user_id": uid}
            os.remove(f'./data/{cid}_{msg_id}')
            time.sleep(1)
            pickle.dump(datos, open(f'./data/{cid}_{msg_id}', 'wb'))
            mostrar_pagina_bl(blackword_list, cid, uid, page, msg_id)
            msg = bot.send_message(msg.chat.id, f"Listo la palabra\n<code>{msg.text}</code>\nse añadió correctamente.", parse_mode="html")

        else:
            bot.send_message(msg.chat.id, f"Acción cancelada")
            bot.clear_step_handler_by_chat_id(uid)



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

#Triggers
ADMIN_IDS = [1221472021, 5579842331, 5174301596]

def is_user_admin(user_id):
    return user_id in ADMIN_IDS or isAdmin(user_id) is not None

@bot.message_handler(commands=['triggers'])
def command_triggers(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if (message.chat.type in ['supergroup', 'group'] or is_user_admin(user_id)):
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status not in ['administrator', 'creator'] and not is_user_admin(user_id):
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
            return

        resul = Triggers.find()
        trigger_list = [doc for doc in resul]  # Usamos comprensión de listas para simplificar el código

        mostrar_pagina(trigger_list, message.chat.id, message.from_user.id, 0, None, message)
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")

def mostrar_pagina(resul, cid, uid=None, pag=0, mid=None, message=None):
    #crear botonera
    markup = InlineKeyboardMarkup(row_width=5)
    b_prev = InlineKeyboardButton("⬅️", callback_data="prev")
    b_close = InlineKeyboardButton("❌", callback_data="close")
    b_next = InlineKeyboardButton("➡️", callback_data="next")
    b_add = InlineKeyboardButton("➕ Agregar Trigger", callback_data="add")
    inicio = pag*ROW_X_PAGE #numero de inicio de la pagina
    fin = pag*ROW_X_PAGE+ROW_X_PAGE #numero del fin de pagina

    mensaje = f"<i>Resultados {inicio+1}-{fin} de {len(resul)}</i>\n\n"
    n = 1
    botones = []
    for trigger in resul[inicio:fin]:
        botones.append(InlineKeyboardButton(str(n), callback_data=str(trigger['_id'])))
        if trigger['eq'] is False:
            mensaje+= f"[<b>{n}</b>] {trigger['triggers']}\n"
        else:
            mensaje+= f"[<b>{n}</b>] {trigger['triggers']} [🌐]\n"
        n+= 1
    markup.row(b_add)
    markup.add(*botones)
    markup.row(b_prev, b_close, b_next)
    if mid:
        bot.edit_message_text(mensaje, cid, mid, reply_markup=markup, parse_mode="html")
    else:
        if cid != uid:
            bot.reply_to(message, "Te escribí por Pv.")
        res = bot.send_message(uid, mensaje, reply_markup=markup, parse_mode="html")
        mid = res.message_id

        datos = {"pag":0, "lista":resul, "user_id": uid}
        pickle.dump(datos, open(f'./data/{uid}_{mid}', 'wb'))

def mostrar_triggers(id_trig, cid, mid):
    #crear botonera
    markup = InlineKeyboardMarkup(row_width=5)
    documento = Triggers.find_one({"_id": ObjectId(id_trig)})
    b_add = InlineKeyboardButton("➕ Agregar Texto", callback_data=f"push_{documento['_id']}")
    b_edit = InlineKeyboardButton("✍️ Editar Trigger", callback_data=f"edit_{documento['_id']}")
    if documento['eq'] is False:
        glbl = InlineKeyboardButton("✅ Hacer Global", callback_data=f"gput_{documento['_id']}")
    else:
        glbl = InlineKeyboardButton("❎ Quitar Global", callback_data=f"gquit_{documento['_id']}")
    b_del = InlineKeyboardButton("⚠️ Eliminar Trigger", callback_data=f"del_{documento['_id']}")
    b_back = InlineKeyboardButton("🔙", callback_data="back")
    b_close = InlineKeyboardButton("❌", callback_data="close")


    mensaje = f"<i>{documento['triggers']:}:</i>\n\n"
    n = 1
    botones = []
    for valor in documento['list_text']:
        e = n - 1
        botones.append(InlineKeyboardButton(str(n), callback_data=f"{id_trig}_{e}"))
        mensaje+= f"[<b>{n}</b>] {valor}\n"
        n+= 1
    n=n-1
    markup.add(*botones)
    if n < 10:
        markup.row(b_add, glbl)
        markup.row(b_edit, b_del)
    markup.row(b_back, b_close)
    bot.edit_message_text(mensaje, cid, mid, reply_markup=markup, parse_mode="html")

def edit_trigger(cid, uid, o_id, pag, mid):
    doc = Triggers.find_one({"_id": ObjectId(o_id)})
    msg = bot.send_message(cid, f"Escribe el reemplazo de <code>{doc['triggers']}</code>:", parse_mode="html")
    bot.register_next_step_handler(msg, catch_trigger, uid, o_id, pag, mid)

def catch_trigger(msg, uid, o_id, pag, mid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Triggers.update_one(
               { "_id" : ObjectId(o_id) },
               { "$set": { "triggers": msg.text } }
            )
            resul = Triggers.find()
            trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
            for doc in resul:
                trigger_list.append(doc) # Agregamos cada documento a la lista
            mostrar_pagina(trigger_list, msg.chat.id, uid, pag, mid)
            bot.send_message(msg.chat.id, f"Trigger editado correctamente")
        else:
            bot.send_message(msg.chat.id, f"Trigger no editado")

def menu_trigger(cid, uid, o_id, sel):
    markup = InlineKeyboardMarkup(row_width=5)
    b_edit = InlineKeyboardButton("✍️ Editar", callback_data=f"edit_{o_id}_{sel}")
    b_del = InlineKeyboardButton("➖ Eliminar", callback_data=f"del_{o_id}_{sel}")
    b_cancel = InlineKeyboardButton("❌ Cancelar", callback_data=f"close")
    markup.row(b_edit, b_del)
    markup.row(b_cancel)
    doc = Triggers.find_one({"_id": ObjectId(o_id)})
    msg = bot.send_message(cid, f"Edición: <code>{doc['list_text'][int(sel)]}</code>\nSelecciona un botón:", reply_markup=markup, parse_mode="html")
    mid = msg.message_id
    datos = {"user_id": uid}
    pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
    #bot.register_next_step_handler(msg, catch_trigger_text, uid, o_id, sel)

def edit_trigger_text(cid, uid, o_id, sel):
    doc = Triggers.find_one({"_id": ObjectId(o_id)})
    msg = bot.send_message(cid, f"Escribe el reemplazo de <code>{doc['list_text'][int(sel)]}</code>:", parse_mode="html")
    bot.register_next_step_handler(msg, catch_trigger_text, uid, o_id, sel)

def catch_trigger_text(msg, uid, o_id, sel):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Triggers.update_one(
               { "_id" : ObjectId(o_id) },
               { "$set": { "list_text." + sel: msg.text } }
            )
            bot.send_message(msg.chat.id, f"Texto editado correctamente")
        else:
            bot.send_message(msg.chat.id, f"Texto no editado")

def del_trigger_text(cid, mid, o_id, sel):
    Triggers.update_one({"_id": ObjectId(o_id)}, {"$unset": {f"list_text.{sel}": 1}})
    Triggers.update_one({"_id": ObjectId(o_id)}, {"$pull": {"list_text": None}})
    os.remove(f'./data/{cid}_{mid}')
    bot.delete_message(cid, mid)
    msg = bot.send_message(cid, f"Texto eliminado")
    time.sleep(5)
    bot.delete_message(cid, msg.message_id)


def add_trigger_text(cid, uid, o_id):
    msg = bot.send_message(cid, f"Escribe el nuevo Texto:")
    bot.register_next_step_handler(msg, catch_new_trigger_text, uid, o_id, cid)

def catch_new_trigger_text(msg, uid, o_id, cid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Triggers.update_one(
               { "_id" : ObjectId(o_id) },
               { "$push": { "list_text": msg.text } }
            )
            msg = bot.send_message(msg.chat.id, f"Texto añadido correctamente")
            time.sleep(5)
            bot.delete_message(cid, msg.message_id)
        else:
            msg = bot.send_message(msg.chat.id, f"Texto no añadido")
            time.sleep(5)
            bot.delete_message(cid, msg.message_id)


def add_trigger(cid, uid, msg_id):
    msg = bot.send_message(uid, f"Escribe el nuevo Trigger:")
    bot.register_next_step_handler(msg, catch_new_trigger, uid, msg_id, cid)

def catch_new_trigger(msg, uid, msg_id, cid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            trigger = msg.text
            msg = bot.send_message(msg.chat.id, f"Listo el trigger\n<code>{msg.text}</code>\nse añadió correctamente.\n Escriba el texto de este trigger:", parse_mode="html")
            bot.register_next_step_handler(msg, catch_new_text_trigger, uid, trigger, msg_id, cid)
        else:
            bot.send_message(msg.chat.id, f"Acción cancelada")
            bot.clear_step_handler_by_chat_id(uid)
    else:
        pass

def catch_new_text_trigger(msg, uid, trigger, msg_id, cid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Triggers.insert_one({ "triggers" : trigger, "list_text": [f"{msg.text}"], "eq": False })
            resul = Triggers.find()
            trigger_list = []
            for doc in resul:
                trigger_list.append(doc)
            page = 0
            datos = {"pag":page, "lista":trigger_list, "user_id": uid}
            os.remove(f'./data/{cid}_{msg_id}')
            time.sleep(1)
            pickle.dump(datos, open(f'./data/{cid}_{msg_id}', 'wb'))
            mostrar_pagina(trigger_list, cid, uid, page, msg_id)
            bot.send_message(msg.chat.id, f"Trigger <code>{trigger}</code> añadido correctamente con el texto <code>{msg.text}</code>", parse_mode="html")
        else:
            bot.send_message(msg.chat.id, f"Acción cancelada")
    else:
        pass

def del_trigger(cid, mid, o_id, uid):
    Triggers.delete_one({"_id": ObjectId(o_id)})
    resul = Triggers.find()
    trigger_list = []
    for doc in resul:
        trigger_list.append(doc)
    page = 0
    datos = {"pag":page, "lista":trigger_list, "user_id": uid}
    os.remove(f'./data/{cid}_{mid}')
    time.sleep(1)
    pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
    mostrar_pagina(trigger_list, cid, uid, page, mid)
    msg = bot.send_message(cid, f"Trigger eliminado")
    time.sleep(5)
    bot.delete_message(cid, msg.message_id)
#End Triggers
    

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

import PIL.Image     

btn_contest = ReplyKeyboardMarkup(
        resize_keyboard=True)
btn_contest.row('Si')
btn_contest.row('No')

@bot.message_handler(content_types=['photo'])
def contest_photo(message):
    contest_num = 1
    if message.chat.type != 'private':
        return
    
    found = False
    for user in contest.find({'contest_num': contest_num}):
        for sub in user['subscription']:
            if sub['user'] == message.from_user.id:
                found = True
                break
                 
    if not found:
        return
    
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(f"func/concurso/{message.from_user.id}.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.send_message(message.chat.id, "Esta imagen es para el concurso?", reply_markup=btn_contest)
    bot.register_next_step_handler(message, confirm_contest_photo, contest_num)
                                       
def confirm_contest_photo(message, contest_num):
        found = False
        for user in contest.find({'contest_num': contest_num}):
            for sub in user['subscription']:
                if sub['user'] == message.from_user.id:
                    found = True

        if found == False:
            return
        
        if message.text != "Si" and message.text != "No":
            msg = bot.send_message(message.chat.id, "Seleccione una respuesta correcta. O escriba 'Si' o 'No'")
            bot.register_next_step_handler(msg, confirm_contest_photo)
        elif message.text == "No":
            msg = bot.send_message(message.chat.id, "Ok pues no...", reply_markup=ReplyKeyboardRemove())
        elif message.text == "Si":
            markup = InlineKeyboardMarkup(row_width=5)
            btns = []
            for i in range(1, 11):
                btn = InlineKeyboardButton(str(i), callback_data=f"contest_vote_{i}_{message.from_user.id}_0")
                btns.append(btn)
            markup.add(*btns)

            content = Contest_Data.find_one({'u_id': message.from_user.id, 'type': 'photo'})

            with PIL.Image.open(f'func/concurso/{message.from_user.id}.jpg') as img:
                msg = bot.send_message(message.chat.id, "Foto subida. Si se desuscribe esta foto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                if not content:
                    #send_data_contest(JUECES, f"Foto de concurso:\n\nVoto:\n", markup, img)
                    msg = bot.send_photo(-1001664356911, img, f"Foto de concurso:\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                    Contest_Data.insert_one({'contest_num': contest_num, 'type': 'photo', 'u_id': message.from_user.id, 'm_id': msg.message_id})
                else:
                    try:
                        bot.delete_message(-1001664356911, content['m_id'])
                    except ApiTelegramException as e:
                        print(e)
                    #send_data_contest(JUECES, f"Foto de concurso actualizada:\n\nVoto:\n", markup, img)
                    msg = bot.send_photo(-1001664356911, img, f"Foto de concurso actualizada:\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                    Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'photo'}, {"$unset": {"vote": ""}})
                    Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'photo'}, {"$set": {'m_id': msg.message_id}})

@bot.message_handler(chat_types=['private']) # You can add more chat types
def command_help(message):
    palabras = message.text.split()
    print(len(palabras))
    if len(palabras) < 200:
        return
    
    contest_num = 1

    found = False
    for user in contest.find({'contest_num': contest_num}):
        for sub in user['subscription']:
            if sub['user'] == message.from_user.id:
                found = True
                break
                 
    if not found:
        return
    text = message.text
    bot.send_message(message.chat.id, "Este texto es para el concurso?", reply_markup=btn_contest)
    bot.register_next_step_handler(message, confirm_contest_text, contest_num, text)

def confirm_contest_text(message, contest_num, text):
        found = False
        for user in contest.find({'contest_num': contest_num}):
            for sub in user['subscription']:
                if sub['user'] == message.from_user.id:
                    found = True

        if found == False:
            return
        
        if message.text != "Si" and message.text != "No":
            msg = bot.send_message(message.chat.id, "Seleccione una respuesta correcta. O escriba 'Si' o 'No'")
            bot.register_next_step_handler(msg, confirm_contest_photo)
        elif message.text == "No":
            msg = bot.send_message(message.chat.id, "Ok pues no...", reply_markup=ReplyKeyboardRemove())
        elif message.text == "Si":
            markup = InlineKeyboardMarkup(row_width=5)
            btns = []
            for i in range(1, 11):
                btn = InlineKeyboardButton(str(i), callback_data=f"contest_vote_{i}_{message.from_user.id}_1")
                btns.append(btn)
            markup.add(*btns)

            content = Contest_Data.find_one({'u_id': message.from_user.id, 'type': 'text'})     
                
            if not content:
                bot.send_message(message.chat.id, "Texto subido. Si se desuscribe este texto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                #send_data_contest(JUECES, f"Texto de concurso:\n\n{text}\n\nVoto:\n", markup)
                msg = bot.send_message(-1001664356911, f"Texto de concurso:\n\n{text}\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                Contest_Data.insert_one({'contest_num': contest_num, 'type': 'text', 'text': text, 'u_id': message.from_user.id, 'm_id': msg.message_id})
            else:
                bot.send_message(message.chat.id, "Texto actualizado. Si se desuscribe este texto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                try:
                    bot.delete_message(-1001664356911, content['m_id'])
                except ApiTelegramException as e:
                    print(e)
                msg = bot.send_message(-1001664356911, f"Texto de concurso actualizado:\n\n{text}\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'text'}, {"$unset": {"vote": ""}})
                Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'text'}, {"$set": {'text': text, 'm_id': msg.message_id}})


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
    
    #Triggers
    if message.chat.type in ['group', 'supergroup']:
        blackwords = []
        for doc in Blacklist.find():
            blackwords.append(doc["blackword"].lower())

        pattern_black = re.compile("|".join(blackwords))

        match_black = pattern_black.search(message.text.lower())

        if match_black:
            warn_user(message, "YES")
            bot.reply_to(message, detected_blackword(message.from_user.username))
            bot.delete_message(message.chat.id, message.message_id)
            return

        triggers = {}
        triggers_equal = {}
        for doc in Triggers.find():
            if "eq" in doc:
                if doc["eq"] is False:
                    triggers_equal[doc["triggers"].lower()] = doc["list_text"]
                if doc["eq"] is True:
                    triggers[doc["triggers"].lower()] = doc["list_text"]

        match = False
        trigger_text = triggers_equal.get(message.text.lower(), None)
        if len(triggers) != 0:
            pattern_trigger = re.compile("|".join(triggers))
            pattern_match = pattern_trigger.search(message.text.lower())
        else:
            pattern_match = None

        if pattern_match:
            trigger = pattern_match.group()
            response = random.choice(triggers[trigger])
            bot.reply_to(message, response)

        if trigger_text:
            match = True
        if match:
            response = random.choice(trigger_text)
            bot.reply_to(message, response)
        
        #Akira AI
        akira_ai(message)

        #AKF
        if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
            user_id = message.reply_to_message.from_user.id
            fst_name = message.reply_to_message.from_user.first_name
            userc_id = message.reply_to_message.chat.id
            user = users.find_one({"user_id": user_id})
        
            if user is not None and "is_afk" in user and int(userc_id) != int(user_id):
                res = f"<b>{fst_name}</b> está AFK"
                if user["reason"]:
                    res += f".\nRazón: {user['reason']}"
                bot.reply_to(message, res, parse_mode='HTML')
         
        # Detectar si el mensaje contiene el @username del cliente
        if hasattr(message, 'entities') and message.entities is not None:
            for entity in message.entities:
                if entity.type == "mention":
                    user_name = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    user = users.find_one({"username": user_name})
        
                    if user is not None:
                        user_id = user.get('user_id', None)
                        user_get = bot.get_chat(user_id)
        
                        if "is_afk" in user:
                            res = f"<b>{user_get.first_name}</b> está AFK"
                            if user["reason"]:
                                res += f".\nRazón: {user['reason']}"
                            bot.reply_to(message, res, parse_mode='HTML')
         
        #Revisar si está afk
        user_id = message.from_user.id
        user = message.from_user
        if not user:  # Ignorar canales
            return
    
        # Verificar si el usuario estaba en modo afk
        user_afk = users.find_one({"user_id": user_id})
         
        if user_afk is not None and "is_afk" in user_afk:
            # Eliminar la entrada de afk de MongoDB
            users.update_one({"user_id": user_id}, {"$unset": {"is_afk": "", "reason": ""}})
            #users.update_one({"user_id": user_id}, {"$unset": {"reason": ""}})
    
            # Enviar un mensaje de bienvenida de vuelta al usuario
            try:
                options = [
                    '{} regresaste calv@!', 'Ah mira volvió {}!', 'Has vuelto {} mamawebo'
                ]
                chosen_option = random.choice(options)
                bot.reply_to(message, chosen_option.format(user.first_name))
            except Exception as e:
                print(f"Error al enviar mensaje de bienvenida: {e}")
        #if match:
        #    trigger = match.group()
        #    # Get a random response for the trigger from the database
        #    response = random.choice(triggers[trigger])
        #    # Send the response to the group or supergroup
        #    bot.reply_to(message, response)
                

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