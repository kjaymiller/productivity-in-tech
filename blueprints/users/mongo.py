from pymongo import MongoClient
from load_config import load_config 
from urllib.parse import quote_plus

cfg = load_config('blueprints/users/config.yml')
db = cfg['db']

(
PASSWORD = quote_plus(db['PASSWORD'])
DATABASE = db['DATABASE']
USERNAME = db['USERNAME']
DATABASE_URL = db['DATABASE_URL']
PORT = db['PORT']

conn = MongoClient(DATABASE_URL, PORT)
db = conn[DATABASE]
#auth = db.authenticate(USERNAME, PASSWORD)