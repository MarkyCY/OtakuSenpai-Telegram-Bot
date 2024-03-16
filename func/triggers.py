import random
import re

def trigger_word(bot, Triggers, message):
    triggers = {}
    triggers_equal = {}
    for doc in Triggers.find():
        if "eq" in doc:
            if doc["eq"] is False:
                triggers_equal[doc["triggers"].lower()] = doc["list_text"]
            if doc["eq"] is True:
                triggers[doc["triggers"].lower()] = doc["list_text"]
     
    match = False
    trigger_text = triggers_equal.get(message.text.lower(), None)
    if len(triggers) != 0:
        pattern_trigger = re.compile("|".join(triggers))
        pattern_match = pattern_trigger.search(message.text.lower())
    else:
        pattern_match = None
     
    if pattern_match:
        trigger = pattern_match.group()
        response = random.choice(triggers[trigger])
        bot.reply_to(message, response)
     
    if trigger_text:
        match = True
    if match:
        response = random.choice(trigger_text)
        bot.reply_to(message, response)