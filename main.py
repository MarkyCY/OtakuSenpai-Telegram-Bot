import telebot
import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()



# Conectarse a la base de datos MongoDB
client = MongoClient('localhost', 27017)
db = client.otakusenpai

#VARIABLES GLOBALES .ENV
Token = os.getenv('BOT_API')

bot = telebot.TeleBot(Token)



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "I'm Alive!!!")


@bot.message_handler(regexp="Hola")
def say_hello(message):
    bot.send_message(message.chat.id, "Holiiii")