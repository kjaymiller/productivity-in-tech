from pymongo import MongoClient


def next_episode_number(collection):
    return collection.count() + 1
