import time
import os
import pickle

from database.mongodb import get_db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from func.list_admins import isAdmin
from bson import ObjectId

db = get_db()
contest = db.contest
Contest_Data = db.contest_data
Triggers = db.triggers
Blacklist = db.blacklist
users = db.users


ADMIN_IDS = [1221472021, 5579842331, 5174301596]

#Cantidad de rows por página en paginación
ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))


def is_user_admin(user_id):
    return user_id in ADMIN_IDS or isAdmin(user_id) is not None


def command_triggers(message, bot):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if (message.chat.type in ['supergroup', 'group'] or is_user_admin(user_id)):
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status not in ['administrator', 'creator'] and not is_user_admin(user_id):
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
            return

        resul = Triggers.find()
        trigger_list = [doc for doc in resul]  # Usamos comprensión de listas para simplificar el código

        mostrar_pagina(bot, trigger_list, message.chat.id, message.from_user.id, 0, None, message)
    else:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")

def mostrar_pagina(bot, resul, cid, uid=None, pag=0, mid=None, message=None):
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

def mostrar_triggers(bot, id_trig, cid, mid):
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

def edit_trigger(bot, cid, uid, o_id, pag, mid):
    doc = Triggers.find_one({"_id": ObjectId(o_id)})
    msg = bot.send_message(cid, f"Escribe el reemplazo de <code>{doc['triggers']}</code>:", parse_mode="html")
    bot.register_next_step_handler(msg, catch_trigger, bot, uid, o_id, pag, mid)

def catch_trigger(msg, bot, uid, o_id, pag, mid):
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
            mostrar_pagina(bot, trigger_list, msg.chat.id, uid, pag, mid)
            bot.send_message(msg.chat.id, f"Trigger editado correctamente")
        else:
            bot.send_message(msg.chat.id, f"Trigger no editado")

def menu_trigger(bot, cid, uid, o_id, sel):
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
    #bot.register_next_step_handler(msg, catch_trigger_text, bot, uid, o_id, sel)

def edit_trigger_text(bot, cid, uid, o_id, sel):
    doc = Triggers.find_one({"_id": ObjectId(o_id)})
    msg = bot.send_message(cid, f"Escribe el reemplazo de <code>{doc['list_text'][int(sel)]}</code>:", parse_mode="html")
    bot.register_next_step_handler(msg, catch_trigger_text, bot, uid, o_id, sel)

def catch_trigger_text(msg, bot, uid, o_id, sel):
    if msg.from_user.id == uid:
        if msg.text is not None:
            Triggers.update_one(
               { "_id" : ObjectId(o_id) },
               { "$set": { "list_text." + sel: msg.text } }
            )
            bot.send_message(msg.chat.id, f"Texto editado correctamente")
        else:
            bot.send_message(msg.chat.id, f"Texto no editado")

def del_trigger_text(bot, cid, mid, o_id, sel):
    Triggers.update_one({"_id": ObjectId(o_id)}, {"$unset": {f"list_text.{sel}": 1}})
    Triggers.update_one({"_id": ObjectId(o_id)}, {"$pull": {"list_text": None}})
    os.remove(f'./data/{cid}_{mid}')
    bot.delete_message(cid, mid)
    msg = bot.send_message(cid, f"Texto eliminado")
    time.sleep(5)
    bot.delete_message(cid, msg.message_id)


def add_trigger_text(bot, cid, uid, o_id):
    msg = bot.send_message(cid, f"Escribe el nuevo Texto:")
    bot.register_next_step_handler(msg, catch_new_trigger_text, bot, uid, o_id, cid)

def catch_new_trigger_text(msg, bot, uid, o_id, cid):
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


def add_trigger(bot, cid, uid, msg_id):
    msg = bot.send_message(uid, f"Escribe el nuevo Trigger:")
    bot.register_next_step_handler(msg, catch_new_trigger, bot, uid, msg_id, cid)

def catch_new_trigger(msg, bot, uid, msg_id, cid):
    if msg.from_user.id == uid:
        if msg.text is not None:
            trigger = msg.text
            msg = bot.send_message(msg.chat.id, f"Listo el trigger\n<code>{msg.text}</code>\nse añadió correctamente.\n Escriba el texto de este trigger:", parse_mode="html")
            bot.register_next_step_handler(msg, catch_new_text_trigger, bot, uid, trigger, msg_id, cid)
        else:
            bot.send_message(msg.chat.id, f"Acción cancelada")
            bot.clear_step_handler_by_chat_id(uid)
    else:
        pass

def catch_new_text_trigger(msg, bot, uid, trigger, msg_id, cid):
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
            mostrar_pagina(bot, trigger_list, cid, uid, page, msg_id)
            bot.send_message(msg.chat.id, f"Trigger <code>{trigger}</code> añadido correctamente con el texto <code>{msg.text}</code>", parse_mode="html")
        else:
            bot.send_message(msg.chat.id, f"Acción cancelada")
    else:
        pass

def del_trigger(bot, cid, mid, o_id, uid):
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
    mostrar_pagina(bot, trigger_list, cid, uid, page, mid)
    msg = bot.send_message(cid, f"Trigger eliminado")
    time.sleep(5)
    bot.delete_message(cid, msg.message_id)