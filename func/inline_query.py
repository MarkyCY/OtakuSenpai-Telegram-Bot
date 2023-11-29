from telebot import types
import telebot
import os
from dotenv import load_dotenv
load_dotenv()

Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)

from pymongo import MongoClient

# Conectar a la base de datos
client = MongoClient('localhost', 27017)
db = client.otakusenpai
animes = db.animes

#peliculas = {
#    #"El castillo ambulante": "Una película de animación japonesa dirigida por Hayao Miyazaki.",
#    #"El viaje de Chihiro": "Una película de animación japonesa dirigida por Hayao Miyazaki.",
#    "Oshi no Ko 2024": "https://t.me/OtakuSenpai2020/251973/1096883",
#    "Sekaiichi Hatsukoi ~Yokozawa Takafumi no Baai~": "https://t.me/OtakuSenpai2020/251973/1097126",
#    "Hunter x Hunter 2012": "https://t.me/OtakuSenpai2020/251973/389702",
#    # Añade más películas aquí...
#}

def query_text(inline_query):
    results = []
    # Busca la consulta en los datos de las películas
    for anime in animes.find({'title': {'$regex': f'.*{str(inline_query.query)}.*', '$options': 'i'}}).limit(10):
        # Crea un resultado de consulta en línea para cada película que coincida
        text=f"⛩️{anime['title']} \n<a href='{anime['link']}'>👁️Ir a ver</a>"
        img="https://cdn.myanimelist.net/s/common/userimages/a1e145b9-8aa0-4538-b365-51aa0a308562_225w?s=4e1e9b009b2035a9ab86669ab22f0091"
        result = types.InlineQueryResultArticle(
            id=anime['title'],  # El primer argumento ahora es 'id', no 'titulo'
            thumbnail_url=img,
            title=anime['title'],
            #description=text,
            url=anime['link'],
            #caption=text,
            #parse_mode="html"
            input_message_content=types.InputTextMessageContent(
                message_text=text,
                parse_mode="HTML"
            )
        )
        results.append(result)
    # Responde a la consulta en línea con los resultados
    bot.answer_inline_query(inline_query.id, results)