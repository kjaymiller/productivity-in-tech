from models import generate_rss_feed, Entry
from db_config import Blog
from sys import argv

from_file = argv[1]

with open(from_file) as f:
    new_post = Entry(from_file=f.read(), collection=Blog)

with open('app/static/' + Blog.collection_name + '.xml', 'w') as f:
    f.write(generate_rss_feed(Blog, atom=True))
