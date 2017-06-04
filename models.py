import re
import pytz
from mongo import db
from urllib.request import urlopen
from datetime import datetime, timezone
from pymongo import ReturnDocument
from markdown import markdown
from bson.objectid import ObjectId

episode_now = datetime.now(pytz.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

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

def total_pages(collection, page=None):
    """Returns a dictionary containing the page navigation"""
    pages = collection.count() // 10 + 1
    if not page or page > pages:
        page = pages

    plus_10 = page + 1
    minus_10 = page - 1
    nav = {'latest': None,
          'minus_10': minus_10,
          'plus_10': plus_10,
          'first': 1,
          'total': pages,
          'current': page}

    return nav


def podcast_page(collection, page=None):
    """returns podcast items for that page"""
    pages = collection.count() // 10 + 1
    if not page or page > pages:
        page = pages

    upper_limit = page * 10
    episodes = []
    collection = collection.find({'episode_number': {'$lte': upper_limit},
                                'published': True},
                                sort=[('episode_number', -1)], limit=10)
    for episode in collection:
        episodes.append(episode)
    return episodes
