from database.mongodb import get_db
import telebot
import os
import time
import pickle

from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from func.list_admins import isAdmin

from dotenv import load_dotenv
load_dotenv()


# Conectar a la base de datos
db = get_db()
Blacklist = db.blacklist

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))
bot = telebot.TeleBot(Token)

def blacklist(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    isadmin = isAdmin(user_id)
    #if user_id == 1221472021 or user_id == 5579842331 or user_id == 5174301596:
    #    isadmin = "Yes"
    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator']:
        if isadmin is not None:
            pass
        else:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
            return

    resul = Blacklist.find()
    blackword_list = [] 
    for doc in resul:
        blackword_list.append(doc) # Agregamos cada documento a la lista

    #bot.send_message(message.chat.id, texto, parse_mode="html")
    mostrar_pagina_bl(blackword_list, message.chat.id, message.from_user.id, 0, None, message)

def mostrar_pagina_bl(resul, cid, uid=None, pag=0, mid=None, message=None):
    #crear botonera
    markup = InlineKeyboardMarkup(row_width=5)
    b_prev = InlineKeyboardButton("⬅️", callback_data="prev_bl")
    b_close = InlineKeyboardButton("❌", callback_data="close")
    b_next = InlineKeyboardButton("➡️", callback_data="next_bl")
    b_add = InlineKeyboardButton("➕ Agregar Palabra", callback_data="add_bw")
    inicio = pag*ROW_X_PAGE #numero de inicio de la pagina
    fin = pag*ROW_X_PAGE+ROW_X_PAGE #numero del fin de pagina

    mensaje = f"<i>Resultados {inicio+1}-{fin} de {len(resul)}</i>\n\n"
    n = 1
    botones = []
    for blackword in resul[inicio:fin]:
        botones.append(InlineKeyboardButton(f"Del: {n}", callback_data=f"bw_{blackword['_id']}"))
        mensaje+= f"[<b>{n}</b>] <span class='tg-spoiler'>{blackword['blackword']}</span>\n"
        n+= 1

    mensaje+= f"\n⚠️Recomendamos no descubrir estas palabras ya que pueden ser ofensivas y de mal gusto."
    markup.row(b_add)
    markup.add(*botones)
    markup.row(b_prev, b_close, b_next)
    if mid:
        bot.edit_message_text(mensaje, cid, mid, reply_markup=markup, parse_mode="html")
    else:
        res = bot.send_message(uid, mensaje, reply_markup=markup, parse_mode="html")
        if cid != uid:
            bot.reply_to(message, "Te escribí por Pv.")

        mid = res.message_id
        datos = {"pag":0, "lista":resul, "user_id": uid}
        pickle.dump(datos, open(f'./data/{uid}_{mid}', 'wb'))

def add_blackword(bot, cid, uid, msg_id):
    msg = bot.send_message(uid, f"Escribe la nueva palabra:")
    bot.register_next_step_handler(msg, catch_new_blackword, bot, uid, msg_id, cid)

def catch_new_blackword(msg, bot, uid, msg_id, cid):
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