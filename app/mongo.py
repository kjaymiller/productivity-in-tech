import pymongo

conn = pymongo.MongoClient('productivityintech.com', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']
extended_coll = db['extended']
friends_coll = db['friends']
