from pymongo import MongoClient
from podcasts import Link, Author, Podcast

# Replace variables with correct information
# database parameters
test_host = 'localhost'
prod_host = 'productivityintech.com'
port = 36161
database = 'pitpodcast'
username = 'kjaymiller'
password = 'a9e4DynzvWFMNe'

conn = MongoClient(prod_host, port)
db = conn[database]
auth = db.authenticate(username, password, source=database)

friends_coll = db['friends']

url = 'http://productivityintech.com'
author = Author('Jay Miller', 'kjaymiller@gmail.com')
class ITunes(Link):
    name = 'iTunes'
    image_path = '/static/images/Get_it_on_iTunes_Badge_US_1114.svg'


class Google(Link):
    name = 'Google'
    image_path = '/static/images/play_en_badge_web_generic.png'


class RSS(Link):
    name = 'RSS'
    image_path = '/static/images/rss.png'


class TuneIn(Link):
    name = 'tunein'


class Stitcher(Link):
    name = 'Stitcher'


class Overcast(Link):
    name = 'Overcast'
    image_path = '/static/images/overcastfm.svg'


class PocketCasts(Link):
    name = 'PocketCasts'
    image_path = '/static/images/pocketcast.png'


PITReflections = Podcast(
    title='Productivity in Tech: Reflections',collection_name='pitreflections',
    url=url, author=author, abbreviation='PIT Reflections', database=db,
    keywords=['journaling', 'productivity', 'reflections', 'thoughts'],
    logo_href="http://static.libsyn.com/p/assets/0/2/4/f/024f9a9f7df1f896/PITReflections.png",
    category="""
        <itunes:category text="Society &amp; Culture">
        	<itunes:category text="Personal Journals"/>
        </itunes:category>
        <itunes:category text="Technology"/>
        <itunes:category text="Society &amp; Culture"/>""",
    summary="""Daily reflections from founder of Productivity in Tech, Jay \
Miller. This podcast was created to encourage you to start thinking about what \
happened in your day and what you can learn from it.""",
    links=[ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-reflections/id1161292423'),
       Google('https://play.google.com/music/listen#/ps/I5essfo5jx2xknxq4vbrmylpjl4'),
       RSS('http://pitreflections.libsyn.com/rss'),
       Overcast('https://overcast.fm/itunes1086437786/the-productivity-in-tech-podcast'),
       PocketCasts('http://pca.st/4f8O'),
       TuneIn('http://tunein.com/radio/PIT-Reflections-p918568/'),
       Stitcher('http://www.stitcher.com/s?fid=101817&refid=stpr')])

PITPodcast = Podcast(title="Productivity in Tech Podcast", abbreviation="PIT",
        keywords=['productivity', 'technology', 'tech', 'success'],
        collection_name='pitpodcast', url=url, author=author, database=db,
        logo_href='http://static.libsyn.com/p/assets/e/e/d/0/eed0db506be5bf2b/center_prod_logo_blue4x.png',
        category="""<itunes:category text="Technology"/>
<itunes:category text="Business"/>
<itunes:category text="Society &amp; Culture"/>""",
        summary="""Weekly podcast where I sit down and talk with people in tech that love productivity.

Or at least love talking about it.""",
        links=[ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-podcast/id1086437786?mt=2'),
               Google('https://play.google.com/music/listen#/ps/Isoopwbe6zdbev5ijenegkcpp44'),
               RSS('https://productivityintech.com/static/pitpodcast.rss'),
               TuneIn('http://tunein.com/radio/Productivity-in-Tech-Podcast-p894677/'),
               Stitcher('http://app.stitcher.com/browse/feed/85598/details')])
