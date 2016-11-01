import re
import pytz
from urllib.request import urlopen
from datetime import datetime
from pymongo import DESCENDING as DES
from markdown import markdown

now = datetime.now(pytz.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

class Link():
    image_path = None

    def __init__(self, url):
        self.url = url

class Podcast():
    """Podcast item"""
    def __init__(self, links, title, abbreviation, collection_name, database, logo_href,
            author, url, category, subtitle='', language='en', keywords=[], **kwargs):
        self.links = links
        self.title = title
        self.collection_name = collection_name
        self.collection = database[collection_name]
        self.abbreviation = abbreviation
        self.keywords = keywords

        # summary and description are interchangable
        sum_in_kwargs = 'summary' in kwargs.keys()
        desc_in_kwargs = 'desc' in kwargs.keys()
        sum_desc = (sum_in_kwargs, desc_in_kwargs)
        if all(sum_desc):
             self.summary = kwargs.get('summary')
             self.description = kwargs.get('description')
        elif any(sum_desc):
            if sum_in_kwargs:
                self.summary = self.description = kwargs.get('summary')
            if desc_in_kwargs:
                self.summary = self.description = kwargs.get('description')
        else:
            self.summary = self.description = ''

        # explicit tag is itunes optional
        if 'explicit' in kwargs.keys():
            self.explicit = '<itunes:explicit>{explicit}</itunes:explicit>'.format(
                kwargs.get(explicit))
        else:
            self.explicit = ''

        self.rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:cc="http://web.resource.org/cc/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<channel>
<atom:link href="{url}/static/{collection_name}.rss" rel="self" type="application/rss+xml"/>
<title>{title}</title>
<pubDate>{date}</pubDate>
<lastBuildDate>{date}</lastBuildDate>
<generator>Productivity in Tech RSS Generator</generator>
<link>{url}/{collection_name}</link>
<language>{language}</language>
<copyright><![CDATA[]]></copyright>
<docs>{url}/{collection_name}</docs>
<itunes:summary><![CDATA[{summary}]]></itunes:summary>
<image>
	<url>{logo_href}</url>
	<title>{title}</title>
	<link><![CDATA[{url}]]></link>
</image>
<itunes:author>{author}</itunes:author>
<itunes:keywords>{keywords}</itunes:keywords>
{category}
<itunes:image href="{logo_href}" />
{explicit}
<itunes:owner>
	<itunes:name><![CDATA[{author}]]></itunes:name>
	<itunes:email>{email}</itunes:email>
</itunes:owner>
<description><![CDATA[{description}]]></description>
<itunes:subtitle><![CDATA[{subtitle}]]></itunes:subtitle>""".format(
    title=title, date=now, collection_name=collection_name, language=language,
    summary=self.summary, logo_href=logo_href, explicit=self.explicit, url=url,
    keywords=','.join(keywords), category=category, email=author.email,
    author=author.name, description=self.description, subtitle=subtitle)

    def generate_rss_feed(self):
        feed = ''
        for item in self.collection.find(sort=[('episode_number', DES)]):
                feed += item['rss']
        return '{podcast}{feed}</channel></rss>'.format(podcast=self.rss, feed=feed)


class Episode():
    """Podcast Episode to be added  object that will be used to add information to the database."""
    def __init__(self, podcast, title,media_url, subtitle='', description='',
                publish_date= now, episode_number=None, **kwargs):
        self.title = title.title()
        self.episode_number = episode_number if episode_number else self.episode_number_from_count()
        self.rss_title = '{} {}:{}'.format(podcast.abbreviation, self.episode_number, self.title)
        self.subtitle = subtitle
        self.media_url = media_url
        self.site_url = 'http://productivityintech.com/{}/{}'.format(podcast.collection.name, self.episode_number)
        self.description = description
        self.length = len(urlopen(media_url).read())
        self.publish_date = publish_date

        # `duration` and `explicit` are not required by itunes rss but should be included when necessary
        if 'duration' in kwargs:
            self.duration = "<itunes:duration>{}</itunes:duration>".format(kwargs.pop('duration'))
        else:
            self.duration = ''

        if 'explicit' in kwargs:
            self.explicit = "<itunes:explicit>{}</itunes:explicit>".format(kwargs.pop('explicit'))
        else:
            self.explicit = ''

        self.rss = """<item>
<title>{title}</title>
<pubDate>{publish_date}</pubDate>
<guid><![CDATA[{site_url}]]></guid>
<link><![CDATA[{site_url}]]></link>
<itunes:image href="http://static.libsyn.com/p/assets/e/e/d/0/eed0db506be5bf2b/center_prod_logo_blue4x.png" />
<description><![CDATA[{description}]]></description>
<enclosure length="{length}" type="audio/mpeg" url="{media_url}" />
{duration}
{explicit}
<itunes:keywords />
<itunes:subtitle><![CDATA[{subtitle}]]></itunes:subtitle>
</item>""".format(title=title, publish_date=publish_date, media_url=media_url,
                  length=self.length, duration=self.duration, explicit=self.explicit,
		          subtitle=subtitle, description=markdown(description), site_url=self.site_url)
        self.__dict__.update(kwargs)

    def episode_number_from_count(self):
        """counts the number of episodes in the mongo collection"""
        return self.collection.count() + 1


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
    collection = collection.find({'episode_number': {'$lte': upper_limit}},
                         sort=[('episode_number', DES)], limit=10)
    for episode in collection:
        episodes.append(episode)
    return episodes
