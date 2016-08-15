from app.mongo import friends_coll
from sys import argv

photos = argv
for photo in photos[1:]:
    print('for {}: '.format(photo))
    name = input('Enter the Name:')
    url = input('url: ')

    with open(photo,'rb') as f:
        photo_file = f.read()

    friend = {
        'name': name,
        'url': url,
        'photo': photo_file
        }

    friends_coll.insert_one(friend)
