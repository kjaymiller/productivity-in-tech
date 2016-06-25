import pymongo
import re

conn = pymongo.MongoClient('localhost', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']
blog_coll = db['blog']


def get_episode(ep_number):
    episode = podcast_coll.find_one({'episode_number': ep_number})
    return episode


def podcast_title(title):
    """Converts the filename to an appropriate title"""
    title = re.sub(r'Released/', r'', title)
    title = title.rstrip('.mp3')
    title = re.sub(r'^ep[_ ]','Ep ', title, re.I)
    first_underscore = title.split('_', 1)
    first_underscore[0] = first_underscore[0] + ': '
    title = str().join(first_underscore)
    title = title.replace('_', ' ')
    title = title.title()
    return title


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    if title.startswith('Ep'):
        result = re.search(r'Ep {0,1}(?P<ep_num>[0-9]+)', title, re.I)
        return result.group('ep_num')


def load_podcast(episode):
        title = podcast_title(episode)
        ep_num = ep_num_file(title)
        url_base='https://s3-us-west-2.amazonaws.com/pitpodcast/'
        episode = {
            'episode_number': int(ep_num),
            'url': url_base + episode,
            'title': title}
        return(episode)


def bulk_load(episode_list):
    for episode in episode_list:
        podcast_coll.insert_one(load_podcast(episode))
