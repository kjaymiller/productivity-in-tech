import pymongo
import re

conn = pymongo.MongoClient('localhost', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']
blog_coll = db['blog']


def get_episode(ep_number):
    episode = podcast_coll.find_one({'episode_number': ep_number})
    return episode


def insert_episode(ep_number, source_url):
    return podcast_coll.insert_one({
                    'episode_number': ep_number,
                    'source_url': source_url})


def podcast_title(title):
    """Converts the filename to an appropriate title"""
    title = title.rstrip('.mp3')
    title = title.replace('ep', 'Episode ')
    first_underscore = title.split('_', 1)
    first_underscore[0] = first_underscore[0] + ': '
    title = str().join(first_underscore)
    title = title.replace('_', ' ')
    title = title.title()
    return title


def get_ep_number_from_file(title):
    """ Retrieves the ep number from the import filename"""
    if title.startswith('ep'):
        result = re.match(r'ep(?P<ep_num>[0-9]+)', title)
        return result.group('ep_num')

    else:
        return
