"""This script loads all of information into our mongoDB."""

from app.mongo import podcast_coll
from app.aws import bucket, all_released, load_podcast


def bulk_load(episode_list):
    for episode in episode_list:
        podcast_coll.insert_one(load_podcast(episode))

episodes = all_released(bucket)
bulk_load(episodes)
