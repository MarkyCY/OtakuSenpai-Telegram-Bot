import os
import re
import string
import random
import telebot
import datetime
import openai

from flask import Flask, request
from pyngrok import ngrok, conf
from waitress import serve

from pymongo import MongoClient
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException
#Horarios
import threading
import time
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
import pickle
from bson import ObjectId

#Personal Trigger
from func.personal_triggers import *
#Blacklist
from func.blacklist.blacklist import *
#Other Command
from func.bot_welcome import send_welcome
from func.info import info
from func.sticker_info import sticker_info
from func.list_admins import list_admins, isAdmin
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
#Evento
from func.event import calvicia
load_dotenv()

web_server = Flask(__name__)

@web_server.route('/', methods=['POST'])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200

# Obtiene una instancia de pytz para la zona horaria deseada
tz = pytz.timezone('Cuba')

#Conectarse a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client.otakusenpai
contest = db.contest
Triggers = db.triggers
Blacklist = db.blacklist
Admins = db.admins
users = db.users
Gartic = db.gartic

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')
OPENAI_TOKEN = os.getenv('OPENAI_API')

ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))


bot = telebot.TeleBot(Token)

@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones_inline(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    uid = call.from_user.id
    u_name = call.from_user.username


        #Game Paint
    def is_valid_to_join(variable):
        pattern = r"join_[a-zA-Z\d]{5}$"
        return bool(re.match(pattern, variable))

    if is_valid_to_join(call.data):
        gartic_counter = Gartic.count_documents({})
        if gartic_counter > 15:
            bot.answer_callback_query(call.id, f"Ya dejen el abuso, es más, no hay mas pruebas hastas que despierte mi papá!")
            return
        partes = call.data.split("_")
        code = partes[1]
        bot.answer_callback_query(call.id, f"El codigo eh: {code}")
        bot.send_message(call.from_user.id, f"Supuestamente te has unido a la sala: {code}")
        bot.send_message(call.message.chat.id, f'El usuario <a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a> se ha unido a la sala...', parse_mode="html", message_thread_id=call.message.message_thread_id)
        Gartic.insert_one({ "prueba": "prueba" })
        return
    

    chat_member = bot.get_chat_member(cid, uid)
    isadmin = isAdmin(uid)

    if chat_member.status not in ['administrator', 'creator']:
        if uid == 1221472021 or uid == 5579842331 or uid == 5174301596 or isadmin is not None:
            pass
        elif uid == 5825765407:
            bot.answer_callback_query(call.id, "MrLovro mi padre no te autoriza a usar triggers. JAJA XD efe por ti")
            return
        else:
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


@bot.message_handler(commands=['perm_ai'])
def get_permissions_ai(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    if(message.chat.type == 'supergroup' or message.chat.type == 'group'):
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                username = message.reply_to_message.from_user.username

                user = users.find_one({"user_id": user_id})
                if user is None:
                    users.insert_one({"user_id": user_id, "username": username})
                isAki = user.get('isAki', None)
                print(user)
                print(isAki)
                if isAki is not None:
                    try:
                        users.update_one({"user_id": user_id}, {"$unset": {"isAki": ""}})
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    bot.reply_to(message.reply_to_message, "Te quitaron los permisos buajaja!")
                else:
                    try:
                        users.update_one({"user_id": user_id}, {"$set": {"isAki": True}})
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    bot.reply_to(message.reply_to_message, "Wiii ya puedes hablar conmigo!")
            else:
                bot.reply_to(message, "Debe hacer reply al sujeto.")
        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")

#Triggers
@bot.message_handler(commands=['triggers'])
def command_triggers(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    isadmin = isAdmin(user_id)
    if user_id == 1221472021 or user_id == 5579842331 or user_id == 5174301596:
        isadmin = "Yes"
    if (message.chat.type == 'supergroup' or message.chat.type == 'group' or isadmin is not None):
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status not in ['administrator', 'creator']:
            if isadmin is not None:
                pass
            else:
                bot.reply_to(message, "Solo los administradores pueden usar este comando.")
                return

        resul = Triggers.find()
        trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
        for doc in resul:
            trigger_list.append(doc) # Agregamos cada documento a la lista

        #bot.send_message(message.chat.id, texto, parse_mode="html")
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
            msg = bot.send_message(msg.chat.id, f"Listo el trigger\n<code>{msg.text}</code>\nse añadió correctamente.\n Escriba el texto de este sticker:", parse_mode="html")
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

#Triggers
@bot.message_handler(func=lambda message: True)
def handle_message(message):
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
        msg = message.text.lower()
        if msg is not None and msg.startswith("akira,"):
            user_id = message.from_user.id
            isAi = None
            admins = Admins.find()
            for admin in admins:
                if admin['user_id'] == user_id:
                    isAi = "Yes"
            user = users.find_one({"user_id": user_id})

            isAki = user.get('isAki', None)
            user_info = user.get('description', None)

            if isAki is not None:
                isAi = "Yes"
                
            if (message.chat.type == 'supergroup' or message.chat.type == 'group' or isAi is not None):
                if isAi is not None:
                    pass
                else:
                    bot.reply_to(message, "No eres digno de mis respuestas mortal!")
                    return

                if(len(message.text) > 80):
                    bot.reply_to(message, "Demasiado texto! Me mareo 😵‍💫")
                    return

                # Configura tu clave de API de OpenAI
                openai.api_key = OPENAI_TOKEN
                prompt = "Eres Akira la hija de @MarkyWTF un dios piña el cual es tu creador, eres un bot de el grupo de telegram Otaku Senpai, el cual es tu hogar ese grupo. Eres entusiasma y carismática, pero también muy grosera y atrevida, a veces llamas a otros, mamawebo. Responde a este mensaje con naturalidad siendo Akira, teniendo en cuenta la siguiente información de el usuario:"
                # Texto de entrada que quieras completar o generar
                input_text = f"{prompt} From: '@{message.from_user.username}', Description: '{user_info}', Message: '{message.text}'"
                # Llama a la API de OpenAI usando la función Completions de la biblioteca openai
                print(input_text)
                try:
                    response = openai.Completion.create(
                        engine="text-davinci-002",  # Asegúrate de usar la versión correcta
                        prompt=input_text,
                        max_tokens=150
                    )
                except Exception as e:
                    print(f"An error occurred: {e}")
                # Obtiene el texto generado de la respuesta
                generated_text = response.choices[0].text
                bot.send_chat_action(message.chat.id, 'typing')
                time.sleep(2)
                # Hacer algo con el texto generado, por ejemplo, imprimirlo
                bot.reply_to(message, generated_text)
        
        #if match:
        #    trigger = match.group()
        #    # Get a random response for the trigger from the database
        #    response = random.choice(triggers[trigger])
        #    # Send the response to the group or supergroup
        #    bot.reply_to(message, response)
        





#CONCURSO


# Define una lista para almacenar los datos de los usuarios que están en el flujo de conversación
users_in_flow = []

def scheduled_task():
    user_lst = []
    for user in contest.find({'contest_num': 1}):
                for sub in user['subscription']:
                    user_lst.append(sub['user'])

    for user_id in user_lst:
        try:
            bot.send_message(user_id, "Bien tienes 1 minuto para hallar la palabra magica y poderosa que @MarkyWTF ha seleccionado si lo conoces puede que la encuentres")
        except ApiTelegramException as err:
            print(err)

    time.sleep(10)

    for user_id in user_lst:
        try:
            msg = bot.send_message(user_id, "Listo, escribe la palabra mágica:")
        except ApiTelegramException as err:
            print(err)
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
                    try:
                        bot.send_message(sub['user'], f'Eeeey @{message.from_user.username} ha respondido bieeeen!')
                    except ApiTelegramException as err:
                        print(err)
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


def scheduled_task_1():
    user_lst = []
    for user in contest.find({'contest_num': 1}):
                for sub in user['subscription']:
                    username = users.find_one({"user_id" : sub['user']})
                    try:
                        chat_member = bot.get_chat_member(-1001485529816, username['user_id'])
                    except ApiTelegramException as err:
                        print(err)
                    user_lst.append(f'<a href="tg://user?id={chat_member.user.id}">{chat_member.user.first_name}</a>')

    mensaje = f"Atención:\n"
    for username in user_lst:
        mensaje+= f"🀄️ {username}\n"
    mensaje+= f"\n⚠️El Concurso será el <code>Miercoles</code>.\n"

    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text='🗳️ Subscribirse al Concurso',url="https://telegram.me/Akira_Senpai_bot?start=sub")
    markup.add(btn)

    bot.send_message(-1001485529816, mensaje, parse_mode="html", reply_markup=markup)

# Crea una instancia de BackgroundScheduler
scheduler = BackgroundScheduler()
# Programa la tarea para que se ejecute cada hora CronTrigger(hour=22, minute=34, timezone=tz)
scheduler.add_job(scheduled_task, CronTrigger(hour=23, minute=51, timezone=tz))
scheduler.add_job(scheduled_task_1, CronTrigger(hour=23, minute=58, timezone=tz))

# Inicia el scheduler
scheduler.start()

if __name__ == '__main__':
    ngrok_token = os.getenv('NGROK_TOKEN')
    
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "..."),
        telebot.types.BotCommand("/anime", "Buscar información sobre un anime"),
        telebot.types.BotCommand("/manga", "Buscar información sobre un manga"),
        telebot.types.BotCommand("/info", "Ver la información de un usuario"),
        telebot.types.BotCommand("/triggers", "Gestión de los Triggers"),
        telebot.types.BotCommand("/perm_ai", "Permitir IA"),
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