from sys import argv
from app.mongo import podcast_coll

photo_url = argv[1]
episode_number = int(input('Enter the Episode Number: '))
podcast_coll.find_one_and_update({'episode_number': episode_number},
                                 {'$set': {'photo': photo_url}},
                                 upsert=True)
