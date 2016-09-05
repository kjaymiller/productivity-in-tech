import pymongo
from app.db_config import host, port, database, username, password

conn = pymongo.MongoClient(host, port)
db = conn[database]
db.authenticate(username, password, source=database)
podcast_coll = db['podcasts']
extended_coll = db['extended']
friends_coll = db['friends']
