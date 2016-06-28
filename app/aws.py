from boto3 import resource
import re

s3 = resource('s3')
bucket = s3.Bucket('pitpodcast')


def podcast_title(title):
    """Converts the filename to an appropriate title"""
    title = re.sub(r'Released/', r'', title)
    title = title.rstrip('.mp3')
    title = re.sub(r'^ep[_ ]', 'Ep ', title, re.I)
    first_underscore = title.split('_', 1)
    first_underscore[0] = first_underscore[0] + ': '
    title = str().join(first_underscore)
    title = title.replace('_', ' ')
    title = title.title()
    return title


def load_podcast(episode):
        title = podcast_title(episode)
        ep_num = ep_num_file(title)
        url_base = 'https://s3-us-west-2.amazonaws.com/pitpodcast/'
        episode = {
            'episode_number': int(ep_num),
            'url': url_base + episode,
            'title': title}
        return(episode)


def all_released(bucket):
    result = []
    for obj in bucket.objects.filter(Prefix='Released'):
        if obj.key.endswith('.mp3'):
            result.append(obj.key)
    return result
