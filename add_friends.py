"""
The add friends tool is designed to create friends of the show
execute this script by 
"""

from db_config import friends_coll

class add_friend():
    def __init__(self, name, photo, url, description, collection=friends_coll):
    self.collection = collection
    self.photo = photo
    self.name = name
    self.url = url
    self.description = description

    with open(photo, 'rb') as f:
        photo_file = f.read()

    def add_friend_to_collection(self):
        return friends_coll.insert_one(self.__dict__())
