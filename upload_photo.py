from models import Episode, generate_rss_feed
from db_config import collections
from sys import argv
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


photo = argv[1]
photoname = photo.split('/')[-1]
scp_file = '/mnt/volume-sfo2-01/files/images/'
ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect('productivityintech.com', username='pituser')

with SCPClient(ssh.get_transport()) as scp:
    scp.put(photo, scp_file)

print('http://productivityintech.com/files/images/' + photname)
