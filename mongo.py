from pymongo import MongoClient
from load_config import cfg
from urllib.parse import quote_plus

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
