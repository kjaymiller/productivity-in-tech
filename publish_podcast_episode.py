from config import PARENT_PATH, RSS_PATH, UPLOAD_PATH
from db_config import collections
from sys import argv
from datetime import datetime
from models import Episode, generate_rss_feed
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import re
import pytz

podcast = argv[1]

def header(val, text, delimit=False):
    re_chk = ': *(.*)$'
    r = re.search('^' + val + re_chk, text, re.I|re.M)

    if r:
        print(r.group(0) + ' found!')
        result = r.group(1)

        if delimit:
            return result.split(',')

        else:
            return result

    else:
        return ''

def strip_headers(text):
    index = 0

    while re.match(r'\w+: *(.*)', text.splitlines()[index]):
        index += 1

    content_lines = text.splitlines()[index:]
    return '\n'.join(content_lines)

podcast_name = podcast.split('_')[0]
episode_number = podcast.split('_')[1]
collection = collections[podcast_name]

rss_path = RSS_PATH + '/{}.rss'.format(podcast_name)
mp3_path = UPLOAD_PATH + '/{}.mp3'.format(podcast)
md_path = PARENT_PATH + '/{}.md'.format(podcast)

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect('productivityintech.com', username='pituser')

with SCPClient(ssh.get_transport()) as scp:
    scp.put(mp3_path, '/mnt/volume-sfo2-01/files/podcast/')


with open(md_path) as f:
    from_file = f.read()

if len(argv) > 2:
    unformatted_date=(argv[2])

else:
    unformatted_date = header('publish_date', text=from_file)

fmt = '%m%d%y %H%M'
d = datetime.strptime(unformatted_date, fmt)
publish_date = d.replace(tzinfo=pytz.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

title = header('title', text=from_file)
subtitle = header('subtitle', text=from_file)
author = header('author', text=from_file)
summary = header('summary', text=from_file)
tags = header('tags', text=from_file, delimit=True)
episode_number = int(header('episode_number', text=from_file))
media_url = header('media_url', text=from_file)
duration = header('duration', text=from_file)
content = strip_headers(from_file)


Episode(collection=collection,
        title=title,
        subtitle=subtitle,
        author=author,
        tags=tags,
        duration=duration,
        summary=summary,
        publish_date=publish_date,
        episode_number=episode_number,
        media_url=media_url,
        content=content)

rss = generate_rss_feed(collection)

with open(rss_path, 'w') as f:
    f.write(rss)

with SCPClient(ssh.get_transport()) as scp:
    scp.put(rss_path, '/mnt/volume-sfo2-01/files/')
