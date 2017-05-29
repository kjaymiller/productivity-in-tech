from pymongo import MongoClient
from config import DATABASE_URL, PORT, DATABASE

conn = MongoClient(DATABASE_URL, PORT)
db = conn[DATABASE]
