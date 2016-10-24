import re
from feedparser import parse
from app.mongo import podcast_coll, pitreflections_coll

feeds = ((podcast_coll, 'http://productivityintech.libsyn.com'),
        (pitreflections_coll, 'http://pitreflections.libsyn.com'))

def parse_feed(collection, feed):
    feed = parse('feed')
    for entry in feed['entries']:
        title = strip_episode_number(feed['title'])
        print(title)


def strip_episode_number(title):
    episode_number = re.search(r'\D+(\d+)', title).group(1)
    return episode_number
