from config import PARENT_PATH, RSS_PATH, UPLOAD_PATH
from db_config import collections
from sys import argv
from datetime import datetime
from models import Episode, generate_rss_feed
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import pytz


podcast = argv[1]

podcast_name = podcast.split('_')[0]
episode_number = podcast.split('_')[1]
collection = collections[podcast_name]

rss_path = RSS_PATH + '/{}.rss'.format(podcast_name)
mp3_path = UPLOAD_PATH + '/{}.mp3'.format(podcast)
md_path = PARENT_PATH + '/{}.md'.format(podcast)

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect('productivityintech.com', username='pituser')
#with SCPClient(ssh.get_transport()) as scp:
#    scp.put(mp3_path, '/mnt/volume-sfo2-01/files/podcast/')

with open(md_path) as f:
    if len(argv) > 2:
        fmt = '%m%d%y %H%M'
        unformatted_date = argv[2]
        d = datetime.strptime(unformatted_date, fmt)
        pub_date = d.replace(tzinfo=pytz.utc).strftime('%a, %d %b %Y %H:%M:%S %z')

        Episode(from_file=f.read(), collection=collection,
                publish_date=pub_date)
    else:
        Episode(from_file=f.read(), collection=collection)

    rss = generate_rss_feed(collection)

with open(rss_path, 'w') as f:
    f.write(rss)

with SCPClient(ssh.get_transport()) as scp:
    scp.put(rss_path, '/mnt/volume-sfo2-01/files/')
