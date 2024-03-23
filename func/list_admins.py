from database.mongodb import get_db


# Conectar a la base de datos
db = get_db()
chat_admins = db.admins
users = db.users


def list_admins(message, bot):
    if (message.chat.type == 'supergroup' or message.chat.type == 'group'):
        # obtén la información del chat
        chat_id = message.chat.id
        #chat_info = bot.get_chat(chat_id)
        # obtén la lista de administradores del chat
        admins = bot.get_chat_administrators(chat_id)

        # Divide a los administradores en propietario y otros administradores
        owner = None
        other_admins = []

        for admin in admins:
            if admin.status == 'creator':
                owner = admin
            elif not admin.user.is_bot:
                other_admins.append(admin)
                # guarda el administrador en la base de datos si no existe
                #if chat_admins.find_one({"user_id": admin.user.id}) is None:
                #    chat_admins.insert_one({"user_id": admin.user.id, "username": admin.user.username})

        # envía un mensaje con la lista de administradores al chat
        message_text = f"👑Propietario:\n└ <a href='https://t.me/{owner.user.username}'>{owner.user.username} > {owner.custom_title}</a>\n\n⚜️ Administradores:"
        
        for user in other_admins[:-1]:
            message_text += f"\n├ <a href='https://t.me/{user.user.username}'>{user.custom_title}</a>"

        if other_admins:
            message_text += f"\n└ <a href='https://t.me/{other_admins[-1].user.username}'>{other_admins[-1].custom_title}</a>"

        bot.send_message(chat_id, message_text, parse_mode='html', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, "Este comando solo puede ser usado en grupos y en supergrupos")



def isAdmin(user_id):
    isAdmin = None
    admins = chat_admins.find()
    for admin in admins:
        if admin['user_id'] == user_id:
            isAdmin = "Yes"
    return isAdmin


def isModerator(user_id):
    isModerator = False
    Users = users.find({"is_mod": True})
    for user in Users:
        if user['user_id'] == user_id:
            isModerator = True
    return isModerator


def set_mod(message, bot):
    if not message.reply_to_message:
        bot.reply_to(message, "Debes hacer reply a un usuario")
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return

    if chat_id != -1001485529816:
        bot.reply_to(message, "Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    filter = {"user_id": reply_user_id}

    try:
        users.update_one(filter, {"$set": {"is_mod": True}}, upsert=True)
    except Exception as e:
        bot.reply_to(message, "Error en la acción.")
        print(f"Error: {e}")
        return

    bot.reply_to(message, "Usuario agregado como colaborador.")
    
def del_mod(message, bot):
    if not message.reply_to_message:
        bot.reply_to(message, "Debes hacer reply a un usuario")
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id

    chat_member = bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Solo los administradores pueden usar este comando.")
        return
    if chat_id != -1001485529816:
        bot.reply_to(message, "Este comando solo puede ser usado en el grupo de OtakuSenpai.")
        return
    
    reply_user_id = message.reply_to_message.from_user.id

    filter = {"user_id": reply_user_id}

    try:
        users.update_one(filter, {"$set": {"is_mod": False}}, upsert=True)
    except Exception as e:
        bot.reply_to(message, "Error en la acción.")
        print(f"Error: {e}")
        return
    
    bot.reply_to(message, f"Usuario eliminado de colaborador.")
