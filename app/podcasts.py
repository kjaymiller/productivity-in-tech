import re
from app.mongo import podcast_coll


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    result = re.search(r'(ep){0,1}[ -]{0,1}(?P<ep_num>[0-9]+)', title, re.I)
    return int(result.group('ep_num'))


def podcast_name(filename):
    remove_dash = re.sub(r'( - )', '_', filename.lower())
    return re.sub(r' ', '_', remove_dash)


def add_shownotes(ep, filename):
    with open(filename) as f:
        notes = f.read()
        result = podcast_coll.find_one_and_update({'episode_number': ep},
                                          {'$set': {'shownotes': notes}})
        return result
