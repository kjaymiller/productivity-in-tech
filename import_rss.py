from app.db_config import PITReflections
from rss import parse_feed
from app.podcasts import rss_pitreflections, generate_rss_feed

feed = 'http://pitreflections.libsyn.com/rss'
coll = PITReflections.collection

parse_feed(coll, feed)
rss = generate_rss_feed(rss_pitreflections, coll)

with open('app/static/pitreflections.rss', 'w') as f:
    f.write(rss)
