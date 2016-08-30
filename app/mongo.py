import pymongo
# from app.config_test import host, port, database  # use in test environment
from app.config import host, port, database

conn = pymongo.MongoClient(host, port)
db = conn[database]
podcast_coll = db['podcasts']
extended_coll = db['extended']
friends_coll = db['friends']
