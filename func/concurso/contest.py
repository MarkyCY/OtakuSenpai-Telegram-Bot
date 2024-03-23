import PIL.Image

from database.mongodb import get_db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telebot.apihelper import ApiTelegramException

btn_contest = ReplyKeyboardMarkup(
        resize_keyboard=True)
btn_contest.row('Si')
btn_contest.row('No')

db = get_db()
contest = db.contest
Contest_Data = db.contest_data

def contest_photo(message, bot):
    contest_num = 1
    if message.chat.type != 'private':
        return
    found = False
    for user in contest.find({'contest_num': contest_num}):
        for sub in user['subscription']:
            if sub['user'] == message.from_user.id:
                found = True
                break
                 
    if not found:
        return
    
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(f"func/concurso/{message.from_user.id}.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    
    bot.send_message(message.chat.id, "Esta imagen es para el concurso?", reply_markup=btn_contest)
    bot.register_next_step_handler(message, confirm_contest_photo, contest_num, bot)
                                       
def confirm_contest_photo(message, contest_num, bot):
        found = False
        for user in contest.find({'contest_num': contest_num}):
            for sub in user['subscription']:
                if sub['user'] == message.from_user.id:
                    found = True

        if found == False:
            return
        
        if message.text != "Si" and message.text != "No":
            msg = bot.send_message(message.chat.id, "Seleccione una respuesta correcta. O escriba 'Si' o 'No'")
            bot.register_next_step_handler(msg, confirm_contest_photo, contest_num, bot)
        elif message.text == "No":
            msg = bot.send_message(message.chat.id, "Ok pues no...", reply_markup=ReplyKeyboardRemove())
        elif message.text == "Si":
            markup = InlineKeyboardMarkup(row_width=5)
            btns = []
            for i in range(1, 11):
                btn = InlineKeyboardButton(str(i), callback_data=f"contest_vote_{i}_{message.from_user.id}_0")
                btns.append(btn)
            markup.add(*btns)

            content = Contest_Data.find_one({'u_id': message.from_user.id, 'type': 'photo'})

            with PIL.Image.open(f'func/concurso/{message.from_user.id}.jpg') as img:
                msg = bot.send_message(message.chat.id, "Foto subida. Si se desuscribe esta foto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                if not content:
                    #send_data_contest(JUECES, f"Foto de concurso:\n\nVoto:\n", markup, img)
                    msg = bot.send_photo(-1001664356911, img, f"Foto de concurso:\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                    Contest_Data.insert_one({'contest_num': contest_num, 'type': 'photo', 'u_id': message.from_user.id, 'm_id': msg.message_id})
                else:
                    try:
                        bot.delete_message(-1001664356911, content['m_id'])
                    except ApiTelegramException as e:
                        print(e)
                    #send_data_contest(JUECES, f"Foto de concurso actualizada:\n\nVoto:\n", markup, img)
                    msg = bot.send_photo(-1001664356911, img, f"Foto de concurso actualizada:\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                    Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'photo'}, {"$unset": {"vote": ""}})
                    Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'photo'}, {"$set": {'m_id': msg.message_id}})


def command_help(message, bot):
    palabras = message.text.split()
    print(len(palabras))
    if len(palabras) < 200:
        return
    
    contest_num = 1

    found = False
    for user in contest.find({'contest_num': contest_num}):
        for sub in user['subscription']:
            if sub['user'] == message.from_user.id:
                found = True
                break
                 
    if not found:
        return
    text = message.text
    bot.send_message(message.chat.id, "Este texto es para el concurso?", reply_markup=btn_contest)
    bot.register_next_step_handler(message, confirm_contest_text, contest_num, text, bot)

def confirm_contest_text(message, contest_num, text, bot):
        found = False
        for user in contest.find({'contest_num': contest_num}):
            for sub in user['subscription']:
                if sub['user'] == message.from_user.id:
                    found = True

        if found == False:
            return
        
        if message.text != "Si" and message.text != "No":
            msg = bot.send_message(message.chat.id, "Seleccione una respuesta correcta. O escriba 'Si' o 'No'")
            bot.register_next_step_handler(msg, confirm_contest_text, contest_num, text, bot)
        elif message.text == "No":
            msg = bot.send_message(message.chat.id, "Ok pues no...", reply_markup=ReplyKeyboardRemove())
        elif message.text == "Si":
            markup = InlineKeyboardMarkup(row_width=5)
            btns = []
            for i in range(1, 11):
                btn = InlineKeyboardButton(str(i), callback_data=f"contest_vote_{i}_{message.from_user.id}_1")
                btns.append(btn)
            markup.add(*btns)

            content = Contest_Data.find_one({'u_id': message.from_user.id, 'type': 'text'})     
                
            if not content:
                bot.send_message(message.chat.id, "Texto subido. Si se desuscribe este texto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                #send_data_contest(JUECES, f"Texto de concurso:\n\n{text}\n\nVoto:\n", markup)
                msg = bot.send_message(-1001664356911, f"Texto de concurso:\n\n{text}\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                Contest_Data.insert_one({'contest_num': contest_num, 'type': 'text', 'text': text, 'u_id': message.from_user.id, 'm_id': msg.message_id})
            else:
                bot.send_message(message.chat.id, "Texto actualizado. Si se desuscribe este texto se eliminará de la base de datos del concurso.", reply_markup=ReplyKeyboardRemove())
                try:
                    bot.delete_message(-1001664356911, content['m_id'])
                except ApiTelegramException as e:
                    print(e)
                msg = bot.send_message(-1001664356911, f"Texto de concurso actualizado:\n\n{text}\n\nVoto:\n", parse_mode="html", reply_markup=markup, message_thread_id=53628)
                Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'text'}, {"$unset": {"vote": ""}})
                Contest_Data.update_one({'u_id': message.from_user.id, 'type': 'text'}, {"$set": {'text': text, 'm_id': msg.message_id}})