from pymongo import MongoClient
from config import DATABASE_URL, USERNAME, PASSWORD, PORT, DATABASE
from urllib.parse import quote_plus

password = quote_plus(PASSWORD)
conn = MongoClient(DATABASE_URL, PORT)
db = conn[DATABASE]
auth = db.authenticate(USERNAME, password)
