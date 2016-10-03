import pymongo
from app.db_config import (prod_host,
                           port,
                           database,
                           username,
                           password)

conn = pymongo.MongoClient(prod_host, port)
db = conn[database]
db.authenticate(username, password, source=database)
podcast_coll = db['podcasts']
pitreflections_coll = db['pitreflections']
extended_coll = db['extended']
friends_coll = db['friends']
