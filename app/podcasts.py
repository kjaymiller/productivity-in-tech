import re
from pymongo import DESCENDING as DES

class Podcast():
    """Podcast object that will be used to add information to the database."""

    def __init__(self, collection, title, url, **kwargs):
        self.collection = collection
        self.episode_number = kwargs.get('episode_number', self.get_ep_number() + 1) # creates the next podcast number
        self.title = title
        self.url = url
        self.description = kwargs.get('description', "I'm sorry but shownotes have not yet been loaded")
        self.links = kwargs.get('links', [])

    def __dict__(self):
        podcast = {}
        podcast['episode_number'] = self.episode_number
        podcast['title'] = self.title
        podcast['url'] = self.url
        podcast['description'] = self.description
        podcast['links'] = []
        return podcast

    def add(self):
        """adds podcast information into the collection"""
        return self.collection.insert_one(self.__dict__())

    def update(self, podcast_info):
        """use to update one or more attributes in of your podcast cannot be"""
        return self.collection.find_one_and_update(
                                                   {'episode_number':self.episode_number},
                                                   {'$set', podcast_info})

    def get_ep_number(self):
        """counts the number of episodes in the mongo collection"""
        return self.collection.count()


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    result = re.search(r'(ep){0,1}[ -]{0,1}(?P<ep_num>[0-9]+)', title, re.I)
    return int(result.group('ep_num'))

def get_episode(collection, episode_number):
    """Returns the episode object from the episode number"""
    return collection.find_one({'episode_number': episode_number})

def podcast_name(filename):
    remove_ep_space = re.sub(r'Ep[ _](?!/d+)', 'ep', filename.lower(), re.I)
    remove_dash = re.sub(r'( - )', '_', remove_ep_space)
    return re.sub(r' ', '_', remove_dash)


def add_shownotes(filename, collection, ep=None):
    with open(filename) as f:
        notes = f.read()
        if not ep:
            ep = ep_num_file(filename)
        result = collection.find_one_and_update({'episode_number': ep},
                                              {'$set': {'shownotes': notes}})
        return result


def last(collection):
    index = collection.count()
    return index


def total_pages(collection, page=None):
    """Returns a dictionary containing the page navigation"""
    pages = last(collection) // 10 + 1
    if not page or page > pages:
        page = pages

    plus_10 = page + 1
    minus_10 = page - 1
    nav = {
        'latest': None,
        'minus_10': minus_10,
        'plus_10': plus_10,
        'first': 1,
        'total': pages,
        'current': page
    }

    return nav


def podcast_page(collection, page=None):
    """returns podcast items for that page"""
    if not page:
        page = last(collection)
    upper_limit = page * 10
    episodes = []
    coll = collection.find({'episode_number': {'$lte': upper_limit}},
                         sort=[('episode_number', DES)], limit=10)
    for episode in coll:
        episodes.append(episode)
    return episodes
