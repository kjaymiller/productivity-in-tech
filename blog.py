from models import Collection
from links import RSS

blog = Collection(
        title='Productivity in Tech Blog',
        collection_name='blog',
        summary='Posts from the Productivity in Tech Blog.',
        links=[RSS('http://productivityintech.com/files/feed.xml')])
