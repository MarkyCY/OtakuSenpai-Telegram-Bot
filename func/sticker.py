import telebot
import math
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image
import os

from dotenv import load_dotenv
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)



def sticker_info(message):
    chat_id = message.chat.id

    # Si el mensaje tiene un reply y es un sticker
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker_id = message.reply_to_message.sticker.file_id
        bot.send_message(chat_id, f"El ID del sticker es: <code>{sticker_id}</code>", reply_to_message_id=message.reply_to_message.message_id, parse_mode="html")

    # Si el mensaje tiene un reply pero no es un sticker
    elif message.reply_to_message and not message.reply_to_message.sticker:
        bot.send_message(chat_id, "Este comando solo puede ser usado con stickers. Por favor, haz reply a un sticker.", reply_to_message_id=message.reply_to_message.message_id)

    # Si el mensaje no tiene un reply
    else:
        bot.send_message(chat_id, "Por favor, haz reply a un sticker para obtener su ID.")

def steal_sticker(message):
    msg = message
    user = msg.from_user
    args = message.text.split(None, 1)
    packnum = 0
    packname = "a" + str(user.id) + "_by_Akira_Senpai_bot"
    print(packname)
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = bot.get_sticker_set(packname)
            print(stickerset.stickers)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = ("a" + str(packnum) + "_" + str(user.id) + "_by_Akira_Senpai_bot")
            else:
                packname_found = 1
        except ApiTelegramException as e:
            if e.result_json['description'] == "Bad Request: STICKERSET_INVALID":
                print("epa")
                packname_found = 1
    stealsticker = "stealsticker.png"
    is_animated = False
    is_video = False
    file_id = ""
    print(msg.reply_to_message.sticker)
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            if msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            bot.reply_to(msg, "No puedo robar eso.")
        
        steal_file = bot.get_file(file_id)
        if is_animated:
            downloaded_file = bot.download_file(steal_file.file_path)
            stealsticker = "stealsticker.tgs"
            with open("stealsticker.tgs", 'wb') as new_file:
                new_file.write(downloaded_file)
        elif is_video:
            downloaded_file = bot.download_file(steal_file.file_path)
            stealsticker = "stealsticker.webm"
            with open("stealsticker.webm", 'wb') as new_file:
                new_file.write(downloaded_file)
        else:
            downloaded_file = bot.download_file(steal_file.file_path)
            stealsticker = "stealsticker.png"
            with open("stealsticker.png", 'wb') as new_file:
                new_file.write(downloaded_file)
        
        if len(args) >= 2:
            sticker_emoji = str(args[1]).split()
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji.split()
        else:
            sticker_emoji = "🤔".split()


        if not is_animated:
            try:
                im = Image.open(stealsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(stealsticker, "PNG")
                bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("stealsticker.png", "rb"),
                    emojis=sticker_emoji
                )
                keyb = [[InlineKeyboardButton('Pack Robao', url=f'https://t.me/addstickers/{packname}')]]
                bot.reply_to(
                    msg,
                    f"Sticker agregado a tu Pack de Stickers."
                    + f"\nEl emoji es: {sticker_emoji}",
                    parse_mode="HTML", 
                    reply_markup=InlineKeyboardMarkup(keyb)
                )

            except OSError as e:
                bot.reply_to(msg, "Solo puedo robar imágenes.")
                print(e)
                return
            
            except ApiTelegramException as e:
                print(e.result_json)
                if e.result_json['description'] == "Bad Request: STICKERSET_INVALID":
                    makepack_internal(
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open("stealsticker.png", "rb"),
                    )

                elif e.result_json['description'] == "Bad Request: can't parse sticker: expected a Unicode emoji":
                        bot.reply_to(msg, "Emoji no válido.")
    
def makepack_internal(
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
):
    name = user.first_name
    name = name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if png_sticker:
            success = bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name} Steal Pack" + extra_version,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            success = bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name} Animated Steal Pack" + extra_version,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )

    except ApiTelegramException as e:
        print(e.result_json)
        if e.message == "El nombre del stickerpack ya está ocupado":
            bot.reply_to(
            msg,
                "Nuevo paquete de sticker creado. Miralo [aquí](https://t.me/addstickers/%s" % packname,
                parse_mode="MARKDOWN",
            )
        elif e.message in ("Peer_id_invalid", "El bot ha sido bloqueado por el usuario"):
            bot.reply_to(
            msg,
                "Contáctame en privado primero.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Iniciar", url=f"t.me/Akira_Senpai_bot")
                ]]),
            )
        elif e.message == "Internal Server Error: created sticker set not found (500)":
            bot.reply_to(
            msg,
            "Paquete de sticker creado siuuu. Miralo [aquí](https://t.me/addstickers/%s" % packname,
            parse_mode="MARKDOWN",
        )  
        return

    if success:
        bot.reply_to(
            msg,
            "Paquete de sticker creado siuuu. Miralo [aquí](https://t.me/addstickers/%s" % packname,
            parse_mode="MARKDOWN",
        )
    else:
        bot.reply_to(
            msg,
            "No pude crear el Pack de Stickers :(")