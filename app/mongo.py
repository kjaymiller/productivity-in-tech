import pymongo

conn = pymongo.MongoClient('localhost', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']
extended_coll = db['extended']
