import pymongo

conn = pymongo.MongoClient('localhost', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']


def get_episode(ep_number):
    episode = podcast_coll.find_one({'episode_number': ep_number})
    return episode['source_url']


def insert_episode(ep_number, source_url):
    return podcast_coll.insert_one({
                    'episode_number': ep_number,
                    'source_url': source_url})
