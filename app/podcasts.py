import re
from app.mongo import podcast_coll as coll


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    result = re.search(r'(ep){0,1}[ -]{0,1}(?P<ep_num>[0-9]+)', title, re.I)
    return int(result.group('ep_num'))


def podcast_name(filename):
    remove_ep_space = re.sub(r'Ep[ _](?!/d+)', 'ep', filename.lower(), re.I)
    remove_dash = re.sub(r'( - )', '_', remove_ep_space)
    return re.sub(r' ', '_', remove_dash)


def add_shownotes(filename, ep=None):
    with open(filename) as f:
        notes = f.read()
        if not ep:
            ep = ep_num_file(filename)
        result = coll.find_one_and_update({'episode_number': ep},
                                          {'$set': {'shownotes': notes}})
        return result
