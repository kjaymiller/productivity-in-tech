import re
import pytz
from itertools import zip_longest
from mongo import db
from urllib.request import urlopen
from datetime import datetime, timezone
from pymongo import ReturnDocument
from markdown import markdown
from bson.objectid import ObjectId

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def last(collection):
    episodes = collection.find({'published': True}, sort=[('publish_date', -1)])
    return episodes[0]

class Link():
    image_path = None

    def __init__(self, url):
        self.url = url

class Collection():
    def __init__(self, title, collection_name, summary, database=db, **kwargs):
        self.title = title
        self.collection = database[collection_name]
        self.collection_name = collection_name
        self.summary = summary
        self.links = kwargs.get('links', [])


class Podcast(Collection):
    """Podcast item"""
    def __init__(self, title, collection_name, summary, logo_href,
            **kwargs):
        super().__init__(title=title, collection_name=collection_name,
                summary=summary)
        self.links = kwargs.get('links', [])
        self.abbreviation = kwargs.get('abbreviation', collection_name)
        self.logo_href = logo_href
        self.logo_small = kwargs.get('logo_small', logo_href)

def latest_post(collection):
    return collection.collection.find_one(sort=[('publish_date', DES)])

def latest_episode(collections):
    episodes = []
    for collection in collections:
        coll = collection.collection
        name = collection.title
        episode = coll.find_one(sort=[('episode_number', DES)])
        episodes.append((name, episode))
    latest_episode = sorted(episodes, key=lambda episode:episode[1]['publish_date'],
            reverse=True)[0]
    latest_episode[1]['name'] = latest_episode[0]
    return latest_episode[1]

def podcast_page(collection, page=0):
    """returns podcast items for that page"""
    episodes = collection.find({'publish_date': {'$lt': episode_now()}}, sort=[('publish_date', -1)])
    pages = list(grouper(episodes, 10))
    if page > len(pages)-1:
        page = -1
    elif page < 0:
        page = -1
    return pages[page]
