import re
from feedparser import parse
from app.podcasts import episode_number_from_title, Podcast

def parse_feed(collection, feed):
    feed = parse(feed)
    collection.drop()
    for entry in feed['entries']:
        episode_number = episode_number_from_title(entry['title'])
        title = strip_episode_from_title(entry['title'])
        description = entry['description']
        subtitle = entry['subtitle']
        duration = entry['itunes_duration']
        publish_date = entry['published']
        media_url = entry.links[1]['href']
        episode = Podcast(title=title, description=description, subtitle=subtitle,
                        media_url=media_url, duration=duration, collection=collection,
                        episode_number=episode_number, publish_date=publish_date)
        collection.insert_one(episode.__dict__)


def strip_episode_from_title(title):
    return re.search('\D+\d+:(.+)', title).group(1)
