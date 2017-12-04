from pymongo import MongoClient
from load_config import load_config 
from urllib.parse import quote_plus

cfg = load_config('config.yml')
db = cfg['db']

(PASSWORD, DATABASE, USERNAME, DATABASE_URL, PORT) = (
		quote_plus(db['PASSWORD']),
		db['DATABASE'],
		db['USERNAME'],
		db['DATABASE_URL'],
		db['PORT'])

conn = MongoClient(DATABASE_URL, PORT)
db = conn[DATABASE]
auth = db.authenticate(USERNAME, PASSWORD)

userdb_connection = MongoClient(DATABASE_URL, 27017)
userdb = userdb_connection['test']
userdb_collection = userdb['test']
