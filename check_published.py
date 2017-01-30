from config import RSS_PATH
from db_config import collections
from datetime import datetime
from models import generate_rss_feed
import pytz

collections = (collections['pitpodcast'], collections['pitreflections'])

for collection in collections:
    db_collection = collection.collection
    for entry in db_collection.find({'published': False}):
        p = datetime.strptime(entry['publish_date'], '%a, %d %b %Y %H:%M:%S %z')
        ep = entry['episode_number']
        if p < datetime.now(pytz.utc):
            db_collection.find_one_and_update({'episode_number': ep},
                    {'$set':{'published': True}})
            print('episode {} published'.format(ep))
        else:
            print('episode {} not yet published'.format(ep))
    rss = generate_rss_feed(collection)


    with open('{}/{}.rss'.format(RSS_PATH, collection.collection_name), 'w+') as f:
        f.write(rss)
