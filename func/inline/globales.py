import re
import pickle
import time
import os

from database.mongodb import get_db
from bson import ObjectId
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from func.videogamedb.api_videogame import get_game
from func.anilist.search_manga import show_manga
from func.anilist.search_anime import show_anime
from func.anilist.search_character import show_character
from func.list_admins import isAdmin

from func.triggers import *
from func.blacklist.blacklist import *

db = get_db()
contest = db.contest
Contest_Data = db.contest_data
Triggers = db.triggers
Blacklist = db.blacklist
users = db.users

JUECES = {938816655, 1881435398, 5602408597, 5825765407, 1221472021, 873919300, 5963355323}

def respuesta_botones_inline(call, bot):
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

    ADMIN_IDS = {1221472021, 5579842331, 5174301596}

    if chat_member.status not in ['administrator', 'creator'] and uid not in ADMIN_IDS and isAdmin(uid) is None:
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
        add_trigger(bot, cid, uid, mid)
        return
    
    if call.data == "add_bw":
        add_blackword(bot, cid, uid, mid)
        return

    if call.data == "back":
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(bot, datos['lista'], cid, uid, datos["pag"], mid)
        return
    
    if call.data == "prev":
        if datos["pag"] == 0:
            bot.answer_callback_query(call.id, "Ya estás en la primera página")
        else:
            datos["pag"]-= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina(bot, datos['lista'], cid, uid, datos["pag"], mid)
        return

    if call.data == "next":
        if datos["pag"] * ROW_X_PAGE + ROW_X_PAGE >= len(datos["lista"]):
            bot.answer_callback_query(call.id, "Ya estás en la ultima página")
        else:
            datos["pag"]+= 1
            pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
            mostrar_pagina(bot, datos["lista"], cid, uid, datos["pag"], mid)
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
        mostrar_triggers(bot, call.data, cid, mid)
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

        menu_trigger(bot, cid, uid, doc['_id'], sel)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(bot, datos["lista"], cid, uid, datos["pag"], mid)
        return

    if is_delete_trigger(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        del_trigger(bot, cid, mid, o_id, uid)
        return
    
    if is_valid_edit_text(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        sel = partes[2]
        os.remove(f'./data/{cid}_{mid}')
        bot.delete_message(cid, mid)
        edit_trigger_text(bot, uid, uid, o_id, sel)
        return
    
    if is_valid_edit(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        edit_trigger(bot, uid, uid, o_id, datos["pag"], mid)
        return
    
    if is_valid_push_trigger(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        add_trigger_text(bot, uid, uid, o_id)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(bot, datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if is_delete_text(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        sel = partes[2]
        del_trigger_text(bot, cid, mid, o_id, sel)
    
    if is_gput_trigger(call.data):
        print("haciendo global")
        partes = call.data.split("_")
        o_id = partes[1]
        Triggers.update_one({'_id': ObjectId(o_id)}, {"$set": {"eq": True}})
        resul = Triggers.find()
        trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
        for doc in resul:
            trigger_list.append(doc) # Agregamos cada documento a la lista
        mostrar_pagina(bot, trigger_list, cid, uid, datos["pag"], mid)
        
    if is_gquit_trigger(call.data):
        print("quitando global")
        partes = call.data.split("_")
        o_id = partes[1]
        Triggers.update_one({'_id': ObjectId(o_id)}, {"$set": {"eq": False}})
        resul = Triggers.find()
        trigger_list = [] # Declaramos una lista vacía para almacenar los triggers
        for doc in resul:
            trigger_list.append(doc) # Agregamos cada documento a la lista
        mostrar_pagina(bot, trigger_list, cid, uid, datos["pag"], mid)