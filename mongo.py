from load_config import load_config 
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
import pytz

def connection_url(mongo_data: dict):
    """
Takes a loaded yaml file and returns a url to connect to. 
THIS DOESN'T ESTABLISH A CONNECTION
"""
    database  = mongo_data['DATABASE']
    database_url = mongo_data['DATABASE_URL']
    
    if all(key in mongo_data for key in ("USERNAME", "PASSWORD")): # I think this is ugly
        username = quote_plus(mongo_data['USERNAME'])
        password = quote_plus(mongo_data['PASSWORD'])
        return f'mongodb://{username}:{password}@{database_url}/{database}'

    else: 
        print("NO USERNAME OR PASSWORD DETECTED. I WOULDN'T RECOMMEND RUNNING THIS IN PROD")
        return f'mongodb://{database_url}/{database}'


content_db_config = load_config('contentdb.yml')
user_db_config = load_config('userdb.yml')

content_database  = content_db_config['DATABASE']
content_port = int(content_db_config['PORT'])
content_connection_url = connection_url(content_db_config)

user_database  = user_db_config['DATABASE']
user_port = int(user_db_config['PORT'])
user_connection_url = connection_url(user_db_config)


content_connection = MongoClient(content_connection_url, content_port)
CONTENT_DB = content_connection[content_database]

user_connection = MongoClient(user_connection_url, user_port) 
USER_DB = user_connection[user_database]

default_sort_direction = [('publish_date', -1)]

def filter_by_date(publish_filter_parameter={'$lt': datetime.now(pytz.utc)}):
  return {'publish_date': publish_filter_parameter}

def get_pages(collection, page, limit):
    """Creates Page Logic for Archives"""
    page_index = (page - 1) * limit
    entries = collection.find(filter_by_date(), sort=default_sort_direction)
    if not entries.count():
        return None

    start_id = entries[page_index]
    date_filter = {'$lte':start_id['publish_date']}
    return collection.find(
        filter_by_date(date_filter), sort=default_sort_direction).limit(limit)

