import re
import pytz
from urllib.request import urlopen
from datetime import datetime, timezone
from pymongo import DESCENDING as DES
from pymongo import ReturnDocument
from markdown import markdown
from bson.objectid import ObjectId

episode_now = datetime.now(pytz.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
atom_now = datetime.now(timezone.utc).astimezone().isoformat()

def last(collection):
    return collection.count({'published': True})


def episode_number_from_count(self):
    """counts the number of episodes in the mongo collection"""
    return self.collection.count() + 1

def generate_rss_feed(collection, atom=False):
    items = ''
    if atom:
        items_list = collection.collection.find({'published': True},
                sort=[('publish_date', DES)])
        for item in items_list:
            items += item['feed']
        return'{channel}{items}</feed>'.format(channel=collection.rss, items=items)

    else:
        items_list = collection.collection.find(sort=[('episode_number', DES)])
        for item in items_list:
            if 'rss' in item.keys():
                items += item['rss']
        return '{channel}{items}</channel></rss>'.format(channel=collection.rss,
                    items=items)

class Link():
    image_path = None

    def __init__(self, url):
        self.url = url

class PodcastAuthor():
    def __init__(self, name, email):
        self.name = name
        self.email = email

class Collection():
    def __init__(self, title, collection_name, subtitle, database, url, uuid='',
                now=atom_now):
        self.title = title
        self.collection_name = collection_name
        self.collection = database[collection_name]
        self.subtitle = subtitle
        self.url = url
        self.rss = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title>{title}</title><subtitle>{subtitle}</subtitle>
<link rel="self" type="application/atom+xml" href="{url}/static/{collection_name}.xml" />
<link rel="alternate" type="text/html" hreflang="en" href="{url}/{collection_name}" />
<updated>{now}</updated><id>urn:uuid:{uuid}</id>""".format(title=title,
        subtitle=subtitle, url=url, collection_name=collection_name,
        now=now, uuid=uuid)


class Podcast(Collection):
    """Podcast item"""
    def __init__(self, title, abbreviation, collection_name, database, url,
                logo_href, author, category, subtitle='', links='', language='en',
                keywords=[], explicit='no', **kwargs):
        super().__init__(title=title, url=url, subtitle=subtitle,
                collection_name=collection_name, database=database)
        self.links = links
        self.abbreviation = abbreviation
        self.summary = kwargs.get('summary', subtitle)
        self.logo_href = logo_href
        if kwargs.get('summary'):
            self.subtitle = ''


        # explicit tag is itunes optional
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
<itunes:summary><![CDATA[{subtitle}]]></itunes:summary>
<image>
	<url>{logo_href}</url>
	<title>{title}</title>
	<link><![CDATA[{url}]]></link>
</image>
<itunes:author>{author}</itunes:author>
<itunes:keywords>{keywords}</itunes:keywords>
{category}
<itunes:image href="{logo_href}" />
<itunes:explicit>{explicit}</itunes:explicit>
<itunes:owner>
	<itunes:name><![CDATA[{author}]]></itunes:name>
	<itunes:email>{email}</itunes:email>
</itunes:owner>
<description><![CDATA[{summary}]]></description>
<itunes:subtitle><![CDATA[{subtitle}]]></itunes:subtitle>""".format(url=url,
        title=title, date=episode_now, collection_name=collection_name,
        logo_href=logo_href, summary= self.summary, explicit=explicit,
        keywords=','.join(keywords), category=category, language=language,
        email=author.email, author=author.name, subtitle=subtitle)


class Entry():
    re_chk = ': *(.*)$'

    def __init__(self, collection, from_file=None, title='', subtitle='', tags=[],
                    author='', summary='', content=None, publish_date=atom_now,
                    podcast=None, check=False, duration=None, explicit=None):
        if from_file:
            self.title = self.header('title', text=from_file)
            self.subtitle = self.header('subtitle', text=from_file)
            self.author = self.header('author', text=from_file)
            self.summary = self.header('summary', text=from_file)
            self.tags = self.header('tags', text=from_file, delimit=True)
            self.content = self.strip_headers(from_file)

        elif all(title, content):
            self.title = title
            self.subtitle = subtitle
            self.tags = tags
            self.content = content
            self.author = author
            self.summary = summary

        self.publish_date = publish_date
        self.collection = c = collection
        c_name = c.collection_name
        self.id = c.collection.insert_one({'title': self.title,
                                          'subtitle': self.subtitle,
                                          'author': self.author,
                                          'summary': self.summary,
                                          'tags': self.tags,
                                          'content': markdown(self.content),
                                          'publish_date': self.publish_date,
                                          'feed': ''}).inserted_id
        url = '{}/{}/{}'.format(c.url, c_name, self.id)
        self.feed = """<entry><title>{title}</title>
<link href="{url}" />
<id>{url}</id>
<author><name>{author}</name></author>
<content><![CDATA[{content}]]></content>
<updated>{publish_date}</updated>
</entry>""".format(title=self.title,
            author=self.author, url=url, content=markdown(self.content),
            publish_date= self.publish_date)
        c.collection.find_one_and_update({'_id':self.id},{'$set':{'feed':self.feed}})



    def header(self, val, text, delimit=False):
        r = re.search('^' + val + self.re_chk, text, re.I|re.M)
        if r:
            print(r.group(0) + ' found!')
            result = r.group(1)
        else:
            return ''

        if delimit:
            result = result.replace(';',',').split(',')
        return result

    def strip_headers(self, text):
        index = 0

        while re.match(r'\w+: *(.*)', text.splitlines()[index]):
            index += 1

        content_lines = text.splitlines()[index:]
        return '\n'.join(content_lines)
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

class Episode(Entry):
    """Podcast Episode to be added  object that will be used to add information to the database."""
    def __init__(self, collection, image_href='', media_url=None, episode_number=None,
                from_file=None, title='', author='', subtitle='', tags=[],
                summary='', content=None, publish_date=episode_now,
                explicit='no', duration=None):

        super().__init__(collection=collection, from_file=from_file,
                title=title, subtitle=subtitle, tags=tags, author=author,
                summary=summary, content=content, publish_date=publish_date)

        pub_datetime = datetime.strptime(publish_date, "%a, %d %b %Y %H:%M:%S %z")
        now = datetime.now(pytz.utc)

        if pub_datetime < now:
            published = True
        else:
            published = False

        if from_file:
            self.episode_number = int(self.header('episode_number', text=from_file))
            self.description = self.strip_headers(text=from_file)
            self.media_url = self.header('media_url', text=from_file)
            self.duration = self.header('duration', text=from_file)

        else:
            self.duration = duration
            self.explicit = explicit
            self.episode_number = last()
            self.media_url= media_url

        c = collection
        if image_href:
            self.image_href = image_href
        else:
            self.image_href = c.logo_href

        url = '{}/{}/{}'.format(c.url, c.collection_name, self.episode_number)
        rss_title = '{} {}: {}'.format(c.abbreviation, self.episode_number, self.title)
        length = len(urlopen(self.media_url).read())

        # `duration` and `explicit` are not required by itunes
        # rss but should be included when necessary
        if 'duration':
            duration = "<itunes:duration>{}</itunes:duration>".format(duration)
        else:
            duration = ''

        if explicit:
            explicit = "<itunes:explicit>{}</itunes:explicit>".format(explicit)
        else:
            explicit = ''
        self.rss = """<item><title>{rss_title}</title>
<pubDate>{publish_date}</pubDate>
<guid><![CDATA[{url}]]></guid>
<link><![CDATA[{url}]]></link>
<itunes:image href="{image_href}" />
<description><![CDATA[{description}]]></description>
<enclosure length="{length}" type="audio/mpeg" url="{media_url}" />
{duration}
{explicit}
<itunes:keywords>{keywords}</itunes:keywords>
<itunes:subtitle><![CDATA[{subtitle}]]></itunes:subtitle>
</item>""".format(rss_title=rss_title, publish_date=publish_date,
            media_url=self.media_url,length=length, duration=self.duration,
            explicit=explicit, subtitle=subtitle, url=url,
            description=markdown(self.description), image_href=self.image_href,
            keywords=(' ').join(self.tags))

        c.collection.find_one_and_update({'_id':self.id},
                {'$set':{'episode_number':self.episode_number,
                'description': self.description, 'media_url':self.media_url,
                'duration': duration, 'image_href':self.image_href,
                'rss':self.rss, 'publish_date':publish_date, 'published':published}})


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
