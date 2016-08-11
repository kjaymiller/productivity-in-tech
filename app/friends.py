"""
Created 8/11/2016
Author: Kevin Miller

Description: Module that manages Friends of the Show page and actions.
"""

from app.aws import bucket
from app.mongo import friends_coll as friends

def make_friend(name, description, photo_path, isperson=False, **kwargs):
    """Creates a friend dictionary object
Name - first if person) name of the friend
Description - description of the friend.
Photo_path - path to photo (Photo will not be saved to )
"""
    friend = {
        'name':name,
        'description': description,
        'url': url,
        'photo': photo_path
    }
    
    if isperson: # persons must contain a last name
        last_name = kwargs.get('last_name', '')
            
            if not last_name:
                raise ValueError("""All persons must have a last_name.""")                
            
            else: 
                last_name['last_name'] = last_name
   
def add_to_friends_list(friend):
    """Add's friend to friends list"""
    return friends.insert_one(friend)