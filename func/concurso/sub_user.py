from pymongo import MongoClient
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.otakusenpai
users = db.users
contest = db.contest

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


def add_user(user_id):
    # Consulta para seleccionar el documento a actualizar
    filter = {'contest_num': 1}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$push': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = contest.update_one(filter, update)

    return result

def del_user(user_id):
    # Consulta para seleccionar el documento a actualizar
    filter = {'contest_num': 1}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$pull': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = contest.update_one(filter, update)

    return result

def reg_user(user_id, username):
    users.insert_one({"user_id": user_id, "username": username})


def subscribe_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    found = False

    if username is None:
        bot.send_message(chat_id, f"Lo siento, no te puedes subscribir al concurso sin un nombre de usuario")
        return
    
    user = users.find_one({'user_id': user_id})
    if user:
        pass
    else:
        reg_user(user_id, username)
    
    for user in contest.find({'contest_num': 1}):
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break
                
            if found:
                bot.send_message(chat_id, f"Oh! Ya estabas registrado en el concurso.")
                break
            
            if not found:
                add_user(user_id)
                bot.send_message(chat_id, f'Bien acabo de registrarte en el concurso @{username}. Para desuscribirte en cualquier momento usa el comando /unsub')


def unsubscribe_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    found = False
    
    user = users.find_one({'user_id': user_id})
    
    for user in contest.find({'contest_num': 1}):
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break
                
            if found:
                del_user(user_id)
                bot.send_message(chat_id, f"Bien te has desuscrito del concurso.")
                break
            
            if not found:
                bot.send_message(chat_id, f'No estás registrado en el concurso')
