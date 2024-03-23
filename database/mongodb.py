import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_db():
    mongo_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongo_uri)
    return client.otakusenpai