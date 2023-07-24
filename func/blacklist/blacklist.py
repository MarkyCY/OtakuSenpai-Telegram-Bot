from pymongo import MongoClient
import telebot
import os
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
import pickle
from bson import ObjectId

from dotenv import load_dotenv
load_dotenv()


# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
Blacklist = db.blacklist

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))
bot = telebot.TeleBot(Token)

def blacklist(message):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        user_id = message.from_user.id
        chat_id = message.chat.id
        chat_member = bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ['administrator', 'creator']:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
            return

        resul = Blacklist.find()
        blackword_list = [] 
        for doc in resul:
            blackword_list.append(doc) # Agregamos cada documento a la lista

        #bot.send_message(message.chat.id, texto, parse_mode="html")
        mostrar_pagina_bl(blackword_list, message.chat.id, message.from_user.id)
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")

def mostrar_pagina_bl(resul, cid, uid=None, pag=0, mid=None):
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
        res = bot.send_message(cid, mensaje, reply_markup=markup, parse_mode="html")
        mid = res.message_id

        datos = {"pag":0, "lista":resul, "user_id": uid}
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))