from telebot import types
import telebot
import os

Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)

peliculas = {
    #"El castillo ambulante": "Una película de animación japonesa dirigida por Hayao Miyazaki.",
    #"El viaje de Chihiro": "Una película de animación japonesa dirigida por Hayao Miyazaki.",
    "Oshi no Ko 2024": "https://t.me/OtakuSenpai2020/251973/1096883",
    "Sekaiichi Hatsukoi ~Yokozawa Takafumi no Baai~": "https://t.me/OtakuSenpai2020/251973/1097126",
    "Hunter x Hunter 2012": "https://t.me/OtakuSenpai2020/251973/389702",
    # Añade más películas aquí...
}

def query_text(inline_query):
    query = inline_query.query
    results = []

    # Busca la consulta en los datos de las películas
    for titulo, link in peliculas.items():
        if query.lower() in titulo.lower():
            # Crea un resultado de consulta en línea para cada película que coincida
            text=f"<b>⛩️{titulo}</b>: \n<a href='{link}'>👁️Ir a ver</a>"
            img="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxYd3qWb7UlM_UBeis23ZV3SHzJpNy9-aBeScMnEzLHO1zc0wD"
            print(titulo)
            result = types.InlineQueryResultArticle(
                id=titulo,  # El primer argumento ahora es 'id', no 'titulo'
                thumbnail_url=img,
                title=titulo,
                description=text,
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