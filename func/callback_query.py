import telebot
import os
import re
import pickle
from pymongo import MongoClient
from bson import ObjectId
from func.triggers.trigg import mostrar_pagina, mostrar_triggers ,menu_trigger ,add_trigger ,det_trigger_text
from dotenv import load_dotenv
load_dotenv()


client = MongoClient('localhost', 27017)
db = client.otakusenpai
Triggers = db.triggers


#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
ROW_X_PAGE = int(os.getenv('ROW_X_PAGE'))
bot = telebot.TeleBot(Token)

def callback_query(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    uid = call.from_user.id

    
    datos = pickle.load(open(f'./data/{cid}_{mid}', 'rb'))

    if datos["user_id"] != uid:
        bot.answer_callback_query(call.id, "Tu no pusiste este comando...")
        return

    if call.data == "close":
        bot.delete_message(cid, mid)
        os.remove(f'./data/{cid}_{mid}')
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
    
    if ObjectId.is_valid(call.data):
        mostrar_triggers(call.data, cid, mid)
        return
    

    def is_valid_edit(variable):
        pattern = r"^[a-f\d]{24}_\d$"
        return bool(re.match(pattern, variable))
    def is_valid_push_trigger(variable):
        pattern = r"^push_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_valid_delete(variable):
        pattern = r"^delete_[a-f\d]{24}$"
        return bool(re.match(pattern, variable))
    def is_delete_text(variable):
        pattern = r"^del_[a-f\d]{24}_\d$"
        return bool(re.match(pattern, variable))

    if is_valid_edit(call.data):
        partes = call.data.split("_")
        o_id = partes[0]
        sel = partes[1]
        doc = Triggers.find_one({"_id": ObjectId(o_id)})

        menu_trigger(cid, uid, doc['_id'], sel)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if is_valid_push_trigger(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        add_trigger(cid, uid, o_id)
        pickle.dump(datos, open(f'./data/{cid}_{mid}', 'wb'))
        mostrar_pagina(datos["lista"], cid, uid, datos["pag"], mid)
        return
    
    if is_delete_text(call.data):
        partes = call.data.split("_")
        o_id = partes[1]
        sel = partes[2]
        det_trigger_text(cid, mid, o_id, sel)