import re
import mutagen
from urllib.request import urlopen
from datetime import datetime
from pymongo import DESCENDING as DES
from markdown import markdown

rss_pitpodcast = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:cc="http://web.resource.org/cc/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<channel>
	<atom:link href="http://productivityintech.com/pitpodcast/rss" rel="self" type="application/rss+xml"/>
	<title>The Productivity in Tech Podcast</title>
	<pubDate>Mon, 17 Oct 2016 12:00:00 +0000</pubDate>
	<lastBuildDate>Thu, 20 Oct 2016 15:20:27 +0000</lastBuildDate>
	<generator>Libsyn WebEngine 2.0</generator>
	<link>http://productivityintech.com</link>
	<language>en</language>
	<copyright><![CDATA[]]></copyright>
	<docs>http://productivityintech.com</docs>
	<itunes:summary><![CDATA[Weekly podcast where I sit down and talk with people in tech that love productivity.

Or at least love talking about it.]]></itunes:summary>
	<image>
		<url>http://static.libsyn.com/p/assets/e/e/d/0/eed0db506be5bf2b/center_prod_logo_blue4x.png</url>
		<title>The Productivity in Tech Podcast</title>
		<link><![CDATA[http://productivityintech.com]]></link>
	</image>
	<itunes:author>Jay Miller</itunes:author>
<itunes:category text="Technology"/>
<itunes:category text="Business"/>
<itunes:category text="Society &amp; Culture"/>
	<itunes:image href="http://static.libsyn.com/p/assets/e/e/d/0/eed0db506be5bf2b/center_prod_logo_blue4x.png" />
	<itunes:explicit>no</itunes:explicit>
	<itunes:owner>
		<itunes:name><![CDATA[Kevin Jay Miller]]></itunes:name>
		<itunes:email>kjaymiller@icloud.com</itunes:email>
	</itunes:owner>
	<description><![CDATA[Weekly podcast where I sit down and talk with people in tech that love productivity.

Or at least love talking about it.]]></description>
	<itunes:subtitle><![CDATA[]]></itunes:subtitle>
"""

rss_pitreflections = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:cc="http://web.resource.org/cc/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<channel>
	<atom:link href="http://pitreflections.libsyn.com/rss" rel="self" type="application/rss+xml"/>
	<title>Productivity in Tech: Reflections</title>
	<pubDate>Fri, 21 Oct 2016 04:32:29 +0000</pubDate>
	<lastBuildDate>Fri, 21 Oct 2016 04:45:17 +0000</lastBuildDate>
	<generator>Libsyn WebEngine 2.0</generator>
	<link>http://pitreflections.libsyn.com/podcast</link>
	<language>en</language>
	<copyright><![CDATA[]]></copyright>
	<docs>http://pitreflections.libsyn.com/podcast</docs>
	<itunes:summary><![CDATA[Daily reflections from founder of Productivity in Tech, Jay Miller. This podcast was created to encourage you to start thinking about what happened in your day and what you can learn from it.]]></itunes:summary>
	<image>
		<url>http://static.libsyn.com/p/assets/0/2/4/f/024f9a9f7df1f896/PITReflections.png</url>
		<title>Productivity in Tech: Reflections</title>
		<link><![CDATA[http://pitreflections.libsyn.com/podcast]]></link>
	</image>
	<itunes:author>Jay Miller</itunes:author>
	<itunes:keywords>journaling,productivity,thoughts</itunes:keywords>
<itunes:category text="Society &amp; Culture">
	<itunes:category text="Personal Journals"/>
</itunes:category>
<itunes:category text="Technology"/>
<itunes:category text="Society &amp; Culture"/>
	<itunes:image href="http://static.libsyn.com/p/assets/0/2/4/f/024f9a9f7df1f896/PITReflections.png" />
	<itunes:explicit>no</itunes:explicit>
	<itunes:owner>
		<itunes:name><![CDATA[Kevin J Miller]]></itunes:name>
		<itunes:email>kjaymiller@gmail.com</itunes:email>
	</itunes:owner>
	<description><![CDATA[Daily reflections from founder of Productivity in Tech, Jay Miller. This podcast was created to encourage you to start thinking about what happened in your day and what you can learn from it.]]></description>
	<itunes:subtitle><![CDATA[]]></itunes:subtitle>
"""


class Podcast():
    """Podcast object that will be used to add information to the database."""
    def __init__(self,
                 collection,
                 duration,
                 title,
                 media_url,
                 subtitle='',
                 description='',
                 explicit='no',
                 pubdate= datetime.now().strftime('%b %d, %Y %H:%M:%s %z')):
        self.collection = collection
        self.episode_number = episode_number if episode_number else self.episode_number_from_count()
        self.rss_title = '{} {}:{}'.format(collection.abbreviation, self.episode_number, title)
        self.subtitle = subtitle
        self.media_url = media_url
        self.site_url = 'http://productivityintech.com/{}/{}'.format(collection, self.episode_number)
        self.description = description
        self.length = urlopen(media_url.read())
        self.duration = duration
        self.pub_date = pub_date
        self.explicit = explicit
        self.rss = """<item>
<title>{title}</title>
<pubDate>{pubdate}</pubDate>
<guid><![CDATA[{site_url}]]></guid>
<link><![CDATA[{site_url}]]></link>
<itunes:image href="http://static.libsyn.com/p/assets/e/e/d/0/eed0db506be5bf2b/center_prod_logo_blue4x.png" />
<description><![CDATA[{description}]]></description>
<enclosure length="{length}}" type="audio/mpeg" url="{media_url}" />
<itunes:duration>{duration}</itunes:duration>
<itunes:explicit>{explicit}}</itunes:explicit>
<itunes:keywords />
<itunes:subtitle><![CDATA[{subtitle}}]]></itunes:subtitle>
</item>""".format(title=title, pubDate=pubDate, media_url=media_url,
                  length=self.length, duration=self.duration,
                  explicit=self.explicit, subtitle=subtitle)
        self.__dict__.update(kwargs)

    def show_duration(self, episode_file):
        """gets mp3 duration length (needed for RSS generation)"""

    def __dict__(self):
        return {'episode_number': self.episode_number,
                'title': self.title,
                'url': self.url,
                'description': self.description,
                'duration': self.duration,
                'subtitle': self.subtitle,
                'media_url':self.media_url,
                'site_url': self.site_url,
                'length': self.length,
                'duration': self.duration,
                'pub_date': self.pub_date,
                'explicit': self.explicit}

    def add(self):
        """adds podcast information into the collection"""
        return self.collection.insert_one(self.__dict__())

    def update(self, podcast_info):
        """use to update one or more attributes in of your podcast cannot be"""
        return self.collection.find_one_and_update(
                                                   {'episode_number':self.episode_number},
                                                   {'$set', podcast_info})

    def episode_number_from_count(self):
        """counts the number of episodes in the mongo collection"""
        return self.collection.count() + 1


def episode_number_from_title(title):
    """ Retrieves the episode number from the title"""
    result = re.search(r'\D+(?P<ep_num>\d+)', title)
    return int(result.group('ep_num'))

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

def generate_rss_feed(podcast, collection):
    feed = ''
    for item in collection.find(sort=[('episode_number', DES)]):
            feed += item['rss']
    return """{podcast}{feed}</channel></rss>""".format(feed)
