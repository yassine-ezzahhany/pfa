import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # charge le .env
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_database()  # accède à pfa_db