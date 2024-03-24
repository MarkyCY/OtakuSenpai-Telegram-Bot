from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import telebot
import os
from dotenv import load_dotenv
load_dotenv()

Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)

from database.mongodb import get_db

# Conectar a la base de datos
db = get_db()
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
    args = inline_query.query.split(" ")
    
    if len(args) == 1:

        try:
            results = [
                InlineQueryResultArticle(
                    id="Anime",
                    title="Anime",
                    description="Buscar Anime",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Anime",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Anime",
                                    switch_inline_query_current_chat='<ANIME> '
                                )
                            ]
                        ]
                    )
                ),
                InlineQueryResultArticle(
                    id="Manga",
                    title="Manga",
                    description="Buscar Manga",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Manga",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Manga",
                                    switch_inline_query_current_chat='<MANGA> '
                                )
                            ]
                        ]
                    )
                ),
                InlineQueryResultArticle(
                    id="Videojuegos",
                    title="Videojuegos",
                    description="Buscar Videojuegos",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Videojuegos",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Videojuegos",
                                    switch_inline_query_current_chat='<GAMES> '
                                )
                            ]
                        ]
                    )
                ),
            ]
        except Exception as e:
            print(e)
    else:
        if args[0] == "<ANIME>":
            results = []
            for anime in animes.find({'title': {'$regex': f'.*{str(args[1])}.*', '$options': 'i'}}).limit(10):
                text=f"⛩️{anime['title']}"
                img="https://i.postimg.cc/Z5sHk6wJ/photo-2023-11-24-08-52-37.jpg"
                result = InlineQueryResultArticle(
                    id=anime['title'],  # El primer argumento ahora es 'id', no 'titulo'
                    thumbnail_url=img,
                    title=f"Anime: {anime['title']}",
                    description=f"Nombre de Anime: {anime['title']}",
                    url=anime['link'],
                    #caption=text,
                    #parse_mode="html"
                    input_message_content=InputTextMessageContent(
                        message_text=text
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Ir a ver",
                                    url=anime['link']
                                )
                            ]
                        ]
                    )
                )
                results.append(result)
            # Responde a la consulta en línea con los resultados

    bot.answer_inline_query(inline_query.id, results)