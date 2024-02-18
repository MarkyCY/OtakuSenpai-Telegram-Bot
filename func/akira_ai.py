import telebot
import os
import colorama
import time
import json
import google.generativeai as genai

from telebot.apihelper import ApiTelegramException
from func.useControl import useControlMongo
from telebot.types import ReactionTypeEmoji

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
users = db.users
Admins = db.admins

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


genai.configure(api_key=os.getenv('GEMINI_API'))
model = genai.GenerativeModel('gemini-pro')

useControlMongoInc = useControlMongo()

def get_permissions_ai(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username

    if message.chat.type not in ['supergroup', 'group']:
        bot.send_message(message.chat.id, f"Este comando solo puede ser usado en grupos y en supergrupos")
        return

    chat_member = bot.get_chat_member(chat_id, user_id)

    if chat_member.status not in ['administrator', 'creator'] and message.from_user.id != 873919300:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Debe hacer reply al sujeto.")
        return

    if user_id != 873919300:
        bot.reply_to(message, "Solo mi padre puede usar ese comando por ahora :(")
        return

    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username

    user = users.find_one({"user_id": user_id})
    if user is None:
        users.insert_one({"user_id": user_id, "username": username})

    if user is not None:
        isAki = user.get('isAki', None)
    else:
        isAki = None
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


def akira_ai(message):
    msg = message.text.lower()
    group_perm = [-1001485529816, -1001664356911, -1001223004404]
    if msg is not None and (msg.startswith("akira,") or msg.startswith("aki,") or msg.startswith("/aki")):
             
        isAi = None
        user_id = message.from_user.id
        isAi = "Yes" if any(admin['user_id'] == user_id for admin in Admins.find()) else None
        user = users.find_one({"user_id": user_id})
        if user is not None:
            isAki = user.get('isAki', None)
            user_info = user.get('description', None)
        else:
            isAki = None
     
        if isAki is not None:
            isAi = "Yes"
     
        if message.chat.id not in group_perm and message.from_user.id != 873919300:
            bot.reply_to(message, "Esta función es exclusiva de Otaku Senpai.")
            return
     
        #if message.chat.type not in ['supergroup', 'group'] or isAi is None:
        #    reaction = ReactionTypeEmoji(type="emoji", emoji="🤡")
        #    bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
        #    bot.reply_to(message, "No eres digno de mis respuestas mortal!")
        #    return
                 
        #Verificar si no se ha llegado al limite de uso
        if useControlMongoInc.verif_limit(user_id) is False and not any(admin['user_id'] == user_id for admin in Admins.find()):
            msg = bot.reply_to(message, "Has llegado al límite de uso diario!")
            reaction = ReactionTypeEmoji(type="emoji", emoji="🥴")
            bot.set_message_reaction(message.chat.id, msg.message_id, reaction=[reaction])
            return
     
        if len(message.text) > 100:
            reaction = ReactionTypeEmoji(type="emoji", emoji="🥴")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
            bot.reply_to(message, "Demasiado texto! Me mareo 😵‍💫")
            return
     
        mention = "None"
        if hasattr(message, 'entities') and message.entities is not None:
            for entity in message.entities:
                if entity.type == "mention":
                    user_name = message.text[entity.offset:entity.offset + entity.length].lstrip('@')
                    user = users.find_one({"username": user_name})
                    if user is not None:
                        descr = user.get('description', '-')
                    else:
                        descr = '-'
                    mention = f"to_username: @{user_name}, description: '{descr}'"
     
        reply = "None"
        if message.reply_to_message and message.reply_to_message.forum_topic_created is None:
            user_id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            #text = message.reply_to_message.text
            user = users.find_one({"user_id": user_id})
            if user is not None:
                descr = user.get('description', None)
            else:
                descr = '-'
            reply = f"to_username: @{username}, description: '{descr}'"
     
        prompt = """
    [Rol] Eres Akira, la hija de @MarkyWTF el cual es tu creador. Eres un bot del grupo de Telegram Otaku Senpai. Eres entusiasta y carismática, pero también muy atrevida. A veces llamas a otros 'caranalga'. Haces mucho Spam de los concursos de dibujo y escritura que hay en el grupo.
    Teniendo en cuenta la siguiente información del usuario:    
    Solo puedes usar estos emojis: ["👍","👎","❤","🔥","🥰","👏","😁","🤔","🤯","😱","🤬","😢","🤩","🤮","💩","🥱","🥴","😍","🤣","💔","🤨","😐","🍾","💋","🖕","😈","😴","😭","🤓"]
    Devuelve todo en formato json con este formato: {message: "respuesta", reaction: "emoji"}".
    """
        input_text = f"{prompt} [From: '@{message.from_user.username}', user_description: '{user_info}', user_message: '{message.text}', mention_to: ['{mention}'], reply_to: ['{reply}']]Responde el texto de user_message como si fueras Akira con textos cortos con formato de mensaje de telegram siguiendo el rol con respuestas naturales y devuelve un texto limpio sin nada que arruine el rol."
     
        colorama.init()
        #print(Fore.BLUE + input_text)
     
        try:
            response = model.generate_content(input_text)
            parts = response.parts
            if parts:
                print(f"response Parts: {response.parts}")
                response = response.candidates[0].content.parts[0].text
            else:
                print(f"response Text: {response.text}")
                response = response.text

        except Exception as e:
            bot.reply_to(message, "Lo siento no puedo atenderte ahora", parse_mode='HTML')
            print(f"An error occurred: {e}")
            return
        reaction = ReactionTypeEmoji(type="emoji", emoji="👨‍💻")
        bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(3)
     

        # Encuentra el índice de inicio y final de la parte JSON
        start_index = response.find('{')
        end_index = response.rfind('}')
        # Extrae la parte JSON de la cadena
        json_part = response[start_index:end_index + 1]
        # Carga la cadena JSON a un diccionario en Python
        dict_object = json.loads(json_part)
     
        text = dict_object["message"]
        print(f"Text: {text}")
        reaction_emoji = dict_object["reaction"]
        print(f"Reaction: {reaction_emoji}")
        try:
            msg = bot.reply_to(message, text, parse_mode='HTML')

            reaction = ReactionTypeEmoji(type="emoji", emoji=reaction_emoji)
            bot.set_message_reaction(message.chat.id, msg.message_id, reaction=[reaction])
     
            #Registrar uso
            useControlMongoInc.reg_use(user_id)
                     
        except ApiTelegramException as err:
            print(err)
            reaction = ReactionTypeEmoji(type="emoji", emoji="💅")
            bot.set_message_reaction(message.chat.id, message.message_id, reaction=[reaction])
            return