from load_config import load_config 
from pymongo import MongoClient
from urllib.parse import quote_plus

def connect_db(mongo_data: dict):
    """
Takes a loaded yaml file and returns a url to connect to. 
THIS DOESN'T ESTABLISH A CONNECTION
"""
    database  = mongo_data['DATABASE']
    database_url = mongo_data['DATABASE_URL']
    port = mongo_data.get('PORT', 27017)
    
    if all(key in mongo_data for key in ("USERNAME", "PASSWORD")): # I think this is ugly
        username = quote_plus(mongo_data['USERNAME'])
        password = quote_plus(mongo_data['PASSWORD'])
        return MongoClient(host=[f'{database_url}:{port}'], username=username, password=password)

    else: 
        print("NO USERNAME OR PASSWORD DETECTED. I WOULDN'T RECOMMEND RUNNING THIS IN PROD")
        return MongoClient(host=[f'{database_url}:{port}'])


content_db_config = load_config('contentdb.yml')
user_db_config = load_config('userdb.yml')

content_connection = connect_db(content_db_config)
CONTENT_DB = content_connection[content_db_config['DATABASE']]

user_connection = connect_db(user_db_config)
USER_DB = user_connection[user_db_config['DATABASE']]
