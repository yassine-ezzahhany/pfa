from pymongo import MongoClient
from core.config import settings

mongo_uri = settings.MONGO_URI
client = MongoClient(mongo_uri)
db = client.get_database(settings.DATABASE_NAME)    # accède à pfa_db