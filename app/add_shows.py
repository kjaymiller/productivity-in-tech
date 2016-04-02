import boto3
import pymongo

conn = pymongo.MongoClient('localhost', 27017)
db = conn['pitpodcast']
podcast_coll = db['podcasts']

# Create connection to aws
s3 = boto3.resource('s3')
s3_pitpodcast = s3.Bucket('pitpodcast')


def podcast_title(title):
    """Converts the filename to an appropriate title"""
    title = title.rstrip('.mp3')
    title = title.replace('ep', 'Episode ')
    first_underscore = title.split('_', 1)
    first_underscore[0] = first_underscore[0] + ': '
    title = str().join(first_underscore)
    title = title.replace('_', ' ')
    title = title.title()
    return title

for object in s3_pitpodcast.objects.all():
    if object.key.startswith('Released/'):
        podcast_file = object.key.split('/')
        if podcast_file[-1]:
            podcast_file = podcast_file[-1]
            podcast = {}
            podcast['filename'] = podcast_file
            podcast['title'] = podcast_title(podcast_file)

            podcast_coll.insert_one(podcast)
