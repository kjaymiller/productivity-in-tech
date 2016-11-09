from models import generate_rss_feed, Entry
from db_config import collections
from sys import argv

collection = collections[argv[2]]
from_file = argv[1]

if len(argv) != 3:
    coll_errs = ','.join(collections.keys())
    raise ValueError('There must be a from_file either {}'.format(coll_errs))

collection.collection.drop()
with open(from_file) as f:
    new_post = Entry(from_file=f.read(), add=True, rss=True, collection=collection)

with open('app/static/' + argv[2] + '.rss', 'w') as f:
    f.write(rss)
