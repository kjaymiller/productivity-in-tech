from boto3 import resource
import re
from mongo import podcast_coll

# Create connection to aws
s3 = resource('s3')
s3_pitpodcast = s3.Bucket('pitpodcast')


def set_ep_number(title):
    if title.startswith('ep'):
        re_ep = re.compile(r'^ep(?P<ep_num>[0-9]+)_')
        result = re.match(re_ep)
        if result and result.groups['ep_num']:
            return result.groups['ep_num']
        else:
            return input('''Title is:
{}.
What is the Episode Number'''.format(title))


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
