import telebot
import time
import os
import PIL.Image 

from telebot.apihelper import ApiTelegramException

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai

users = db.users
Contest_Data = db.contest_data

# Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)




def calvicia(uid, seconds):
    try:
        bot.send_message(uid, f"Ha(n) pasado {seconds} segundo(s)")
    except ApiTelegramException as err:
        print(err)


def contest_event(message):
    to_forum = 251988
    to_chat_id = -1001485529816

    #Test
    #to_chat_id = -1001664356911
    #to_forum = 58139

    text_res = []
    img_res = []

    print(os.getenv('MONGO_URI'))
    if message.from_user.id != 873919300:
        return
    
    res_text = Contest_Data.find({"type": "text"})
    res_img = Contest_Data.find({"type": "photo"})
    #Anuncio y cierre de temas
    forums = [252001, 594583, 251985, 342257, 253659, 252051, 251977, 253687, 251988, 251980, 251973]
    #forums = [58139]
    
    try:
        bot.close_general_forum_topic(to_chat_id)
    except Exception as e:
        print(e)
    bot.send_message(to_chat_id, "Psss wapo ve para el tópico de <a href='https://t.me/OtakuSenpai2020/251988'>Concursos</a> que vamos a empezar en unos minutos", parse_mode="html")

    for forum in forums:
        try:
            bot.close_forum_topic(to_chat_id, forum)
        except Exception as e:
            print(e)

        bot.send_message(to_chat_id, "Psss wapo ve para el tópico de <a href='https://t.me/OtakuSenpai2020/251988'>Concursos</a> que vamos a empezar en unos minutos", parse_mode="html", message_thread_id=forum)
        time.sleep(3)

    #time.sleep(120)
    time.sleep(6)

    #Anuncio fin

    bot.send_message(to_chat_id, "Bieeeen atención vamos a mostrar los resultados del concurso wiiiii.", message_thread_id=to_forum)
    time.sleep(20)
    bot.send_message(to_chat_id, "Vale empecémos! Primeramente con las narraciones!", message_thread_id=to_forum)
    time.sleep(10)

    for i, doc in enumerate(res_text):
        if i == 0:
            bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Jl4SXInzn1xmMHuL6L_vmFtywzYwACMgUAAlRHKEZ58qEMwbw7TDQE", message_thread_id=to_forum)
            bot.send_message(to_chat_id, 'Empezaremos con...', message_thread_id=to_forum)
        if i == 1:
            bot.send_message(to_chat_id, 'Le sigue:', message_thread_id=to_forum)
        if i == 2:
            bot.send_message(to_chat_id, 'Y ahora tenemos a:', message_thread_id=to_forum)
        if i == 3:
            bot.send_message(to_chat_id, 'Juju seguimos con:', message_thread_id=to_forum)
        if i == 4:
            bot.send_message(to_chat_id, 'Wiiii vamonos con:', message_thread_id=to_forum)
        if i == 5:
            bot.send_message(to_chat_id, 'Ahora presento a:', message_thread_id=to_forum)
        if i == 6:
            bot.send_message(to_chat_id, 'Wow no puede ser le toca a:', message_thread_id=to_forum)
        if i == 7:
            bot.send_message(to_chat_id, 'Vaia vaia, mira quien va:', message_thread_id=to_forum)
        if i == 8:
            bot.send_message(to_chat_id, 'Ah estabamos esperandote...', message_thread_id=to_forum)
        if i == 9:
            bot.send_message(to_chat_id, 'Sigue', message_thread_id=to_forum)
        if i == 10:
            bot.send_message(to_chat_id, 'Estoy cansada cuando termina... Va', message_thread_id=to_forum)
        if i == 11:
            bot.send_message(to_chat_id, 'Este es bien mamawebo, vas tu', message_thread_id=to_forum)
        if i == 12:
            bot.send_message(to_chat_id, 'Jmmm ya vas tu:', message_thread_id=to_forum)
        if i == 13:
            bot.send_message(to_chat_id, 'Tututu... Ah cierto! Ahora vas tu!', message_thread_id=to_forum)

        chat_member = bot.get_chat_member(-1001485529816, doc['u_id'])
        time.sleep(10)

        if chat_member.user.username is not None:
            bot.send_message(to_chat_id, f"<a href='https://t.me/{chat_member.user.username}'>{chat_member.user.username}</a>", parse_mode="html", message_thread_id=to_forum)
        else:
            bot.send_message(to_chat_id, f"<a href='tg://user?id={chat_member.user.id}'>{chat_member.user.first_name}</a>", parse_mode="html", message_thread_id=to_forum)

        if(doc.get('vote')):
            votos = doc["vote"]
            suma = sum(votos.values())
            num = len(votos)
            prom = (suma / num)
        
        add_tuple = (chat_member.user.username, round(prom, 1))
        text_res.append(add_tuple)

        time.sleep(10)
        #content = Contest_Data.find_one({'u_id': doc['u_id']})

        bot.send_message(to_chat_id, f"Su obra:", message_thread_id=to_forum)
        time.sleep(3)
        if doc['u_id'] == 5120872311:
            bot.forward_message(from_chat_id=-1001664356911, message_id=57028, chat_id=to_chat_id, message_thread_id=to_forum)
            bot.forward_message(from_chat_id=-1001664356911, message_id=57029, chat_id=to_chat_id, message_thread_id=to_forum)
        else:
            bot.send_message(to_chat_id, f"{doc['text']}", message_thread_id=to_forum)

        bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Jl4SXInzn1xmMHuL6L_vmFtywzYwACMgUAAlRHKEZ58qEMwbw7TDQE", message_thread_id=to_forum)
        time.sleep(20)

    text_res.sort(key=lambda x: x[1], reverse=True)

    anunc = "Este es el promedio por votaciones del concurso de narración:"
    for i, tupla in enumerate(text_res):
        if i == 0:
            winner = tupla[0]
        anunc += f"\n@{tupla[0]} con <span class='tg-spoiler'>{tupla[1]}/10</span>"
        print(winner)

    bot.send_message(to_chat_id, anunc, parse_mode="html", message_thread_id=to_forum)
    time.sleep(5)
    bot.send_message(to_chat_id, f"La persona ganadora es @{winner} Felicidades!!!", parse_mode="html", message_thread_id=to_forum)
    bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Nl4SXUEEshkmME3YzHEpANGnZ-3QACTQUAAnhGKUaVOtfYYMI7YjQE", message_thread_id=to_forum)
    
    time.sleep(20)

    bot.send_message(to_chat_id, "Ahora vamos con los dibujos!", message_thread_id=to_forum)
    time.sleep(10)

    for i, doc in enumerate(res_img):

        if i == 0:
            bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Jl4SXInzn1xmMHuL6L_vmFtywzYwACMgUAAlRHKEZ58qEMwbw7TDQE", message_thread_id=to_forum)
            bot.send_message(to_chat_id, 'Vamos a empezar con...', message_thread_id=to_forum)
        if i == 1:
            bot.send_message(to_chat_id, 'Luego tenemos a:', message_thread_id=to_forum)
        if i == 2:
            bot.send_message(to_chat_id, 'Y ahora sigue:', message_thread_id=to_forum)
        if i == 3:
            bot.send_message(to_chat_id, 'Juju seguimos con:', message_thread_id=to_forum)
        if i == 4:
            bot.send_message(to_chat_id, 'Wiiii vamonos con:', message_thread_id=to_forum)
        if i == 5:
            bot.send_message(to_chat_id, 'Ahora presento a...', message_thread_id=to_forum)
        if i == 6:
            bot.send_message(to_chat_id, 'Wow no puede ser le toca a:', message_thread_id=to_forum)
        if i == 7:
            bot.send_message(to_chat_id, 'Vaia vaia, mira quien va...', message_thread_id=to_forum)
        if i == 8:
            bot.send_message(to_chat_id, 'Ah estabamos esperandote...', message_thread_id=to_forum)
        if i == 9:
            bot.send_message(to_chat_id, 'Estoy cansada cuando termina esto? Ahora va', message_thread_id=to_forum)
        if i == 10:
            bot.send_message(to_chat_id, 'Ahora me dicen que va...', message_thread_id=to_forum)
        if i == 11:
            bot.send_message(to_chat_id, 'Este es bien mamawebo, vas tu', message_thread_id=to_forum)
        if i == 12:
            bot.send_message(to_chat_id, 'Tututu... Ah cierto! Ahora vas tu!', message_thread_id=to_forum)

        chat_member = bot.get_chat_member(-1001485529816, doc['u_id'])
        time.sleep(2)

        if chat_member.user.username is not None:
            bot.send_message(to_chat_id, f"<a href='https://t.me/{chat_member.user.username}'>{chat_member.user.username}</a>", parse_mode="html", message_thread_id=to_forum)
        else:
            bot.send_message(to_chat_id, f"<a href='tg://user?id={chat_member.user.id}'>{chat_member.user.first_name}</a>", parse_mode="html", message_thread_id=to_forum)

        if(doc.get('vote')):
            votos = doc["vote"]
            suma = sum(votos.values())
            num = len(votos)
            prom = (suma / num)

        add_tuple = (chat_member.user.username, round(prom, 1))
        img_res.append(add_tuple)
        
        #content = Contest_Data.find_one({'u_id': doc['u_id']})

        bot.send_message(to_chat_id, f"Su obra:", message_thread_id=to_forum)
        with PIL.Image.open(f'func/concurso/{chat_member.user.id}.jpg') as img:
            bot.send_photo(to_chat_id, img, message_thread_id=to_forum)

        bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Jl4SXInzn1xmMHuL6L_vmFtywzYwACMgUAAlRHKEZ58qEMwbw7TDQE", message_thread_id=to_forum)
        time.sleep(5)

    
    img_res.sort(key=lambda x: x[1], reverse=True)

    anunc = "Y ahora el promedio por votaciones del concurso de dibujo:"
    for i, tupla in enumerate(img_res):
        if i == 0:
            winner = tupla[0]
        anunc += f"\n@{tupla[0]} con <span class='tg-spoiler'>{tupla[1]}/10</span>"
        print(winner)
        
    #Finalizar con Anuncio de ganador

    bot.send_message(to_chat_id, anunc, parse_mode="html", message_thread_id=to_forum)
    time.sleep(10)
    bot.send_message(to_chat_id, f"La persona ganadora es @{winner} Felicidades!!!", parse_mode="html", message_thread_id=to_forum)
    bot.send_sticker(to_chat_id, sticker="CAACAgEAAx0CYzQSLwAC47Nl4SXUEEshkmME3YzHEpANGnZ-3QACTQUAAnhGKUaVOtfYYMI7YjQE", message_thread_id=to_forum)
    time.sleep(10)
    bot.send_message(to_chat_id, f"Muchas gracias a todos por estar aquí y gracias a los concursantes por participar y por sus geniales obras. Ya volveremos con otro super evento próximamente.", parse_mode="html", message_thread_id=to_forum)
    #Abrir Temas
    bot.reopen_general_forum_topic(to_chat_id)
    bot.send_message(to_chat_id, "Evento terminado mua los quiero mamawebos", parse_mode="html")
    for forum in forums:
        time.sleep(3)
        bot.reopen_forum_topic(to_chat_id, forum)
        bot.send_message(to_chat_id, "Evento terminado mua los quiero mamawebos", parse_mode="html", message_thread_id=forum)
