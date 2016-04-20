from boto3 import resource
from mongo import podcast_coll
from tools import rename_file

# Create connection to aws
s3 = resource('s3')
s3_pitpodcast = s3.Bucket('pitpodcast')

for object in s3_pitpodcast.objects.all():
    if object.key.startswith('Released/'):
        podcast_file = object.key.split('/')
        if podcast_file[-1]:
            podcast_file = podcast_file[-1]
            podcast = {}
            podcast['filename'] = podcast_file
            podcast['title'] = rename_file.podcast_title(podcast_file)

            podcast_coll.insert_one(podcast)
