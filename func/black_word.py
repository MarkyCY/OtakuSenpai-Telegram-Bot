import re
from func.admin.warn import warn_user
from func.personal_triggers import *

def black_word(bot, Blacklist, message):
    blackwords = []
    for doc in Blacklist.find():
        blackwords.append(doc["blackword"].lower())
     
    pattern_black = re.compile("|".join(blackwords))
     
    match_black = pattern_black.search(message.text.lower())
     
    if match_black:
        warn_user(message, "YES")
        bot.reply_to(message, detected_blackword(message.from_user.username))
        bot.delete_message(message.chat.id, message.message_id)
        return