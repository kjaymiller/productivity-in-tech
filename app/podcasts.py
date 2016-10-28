import re
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
	<generator>Productivity in Tech RSS</generator>
	<link>http://productivityintech.com/pitpodcast</link>
	<language>en</language>
	<copyright><![CDATA[]]></copyright>
	<docs>http://productivityintech.com/pitpodcast</docs>
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


class Episode():
    """Podcast Episode to be added  object that will be used to add information to the database."""
    def __init__(self, episode_title, collection_name, media_url, subtitle='', description='',
                publish_date= datetime.now().strftime('%b %d, %Y %H:%M:%S %z'), 
                episode_number=None, **kwargs):
        self.episopde_title = episode_title.title()
        self.collection_name = collection_name.lower()
        self.episode_number = episode_number if episode_number else self.episode_number_from_count()
        self.rss_title = '{} {}:{}'.format(collection.abbreviation, self.episode_number, title)
        self.subtitle = subtitle
        self.media_url = media_url
        self.site_url = 'http://productivityintech.com/{}/{}'.format(collection.name, self.episode_number)
        self.description = markdown(description)
        self.length = len(urlopen(media_url).read())
        self.publish_date = publish_date
        
        # `duration` and `explicit` are not required by itunes rss but should be included when necessary 
        if 'duration' in kwargs:
            self.duration = "<itunes:duration>{}</itunes:duration>".format(duration)
        else:
            self.duration = ''
        
        if 'explicit' in kwargs:
            self.explicit = "<itunes:explicit>{}</itunes:explicit>".format(explicit)
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
{<itunes:keywords />}
<itunes:subtitle><![CDATA[{subtitle}]]></itunes:subtitle>
</item>""".format(title=title, publish_date=publish_date, media_url=media_url,
                  length=self.length, duration=self.duration, explicit=self.explicit, 
		  subtitle=subtitle, description=description, site_url=self.site_url)
        self.__dict__.update(kwargs)

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
