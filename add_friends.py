from app.mongo import friends_coll
from sys import argv
from json import loads

with open(argv[1]) as f:
    friend_file = loads(f.read())

photo = friend_file['photo']
name = friend_file['name']
url = friend_file['url']
description = friend_file['description']

with open(photo, 'rb') as f:
    photo_file = f.read()

friend = {
    'name': name,
    'url': url,
    'photo': photo_file,
    'description': description
    }

friends_coll.insert_one(friend)
