import os
import sqlite3
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "novha.db")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "novha_db")

def get_sql():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

_mongo_client = None
def get_mongo():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _mongo_client[MONGO_DB]