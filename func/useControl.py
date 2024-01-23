from pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

Limit = os.getenv('LIMIT_USE')

class useControlMongo:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["otakusenpai"]
        self.collection = self.db["count_use"]

    def verif_limit(self, user_id):
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")  # Convertir la fecha a una cadena
        user_key = {"user_id": user_id, "date": today_str}
        user_record = self.collection.find_one(user_key)

        if user_record is None:
            user_record = {"user_id": user_id, "date": today_str, "count": 0}
            self.collection.insert_one(user_record)

        return user_record["count"] < int(Limit)

    def reg_use(self, user_id):
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")  # Convertir la fecha a una cadena
        user_key = {"user_id": user_id, "date": today_str}
        self.collection.update_one(user_key, {"$inc": {"count": 1}}, upsert=True)
