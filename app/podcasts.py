import re
from app.mongo import podcast_coll
from pymongo import DESCENDING as DES


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    result = re.search(r'(ep){0,1}[ -]{0,1}(?P<ep_num>[0-9]+)', title, re.I)
    return int(result.group('ep_num'))


def podcast_name(filename):
    remove_ep_space = re.sub(r'Ep[ _](?!/d+)', 'ep', filename.lower(), re.I)
    remove_dash = re.sub(r'( - )', '_', remove_ep_space)
    return re.sub(r' ', '_', remove_dash)


def add_shownotes(filename, database=podcast_coll, ep=None):
    with open(filename) as f:
        notes = f.read()
        if not ep:
            ep = ep_num_file(filename)
        result = database.find_one_and_update({'episode_number': ep},
                                              {'$set': {'shownotes': notes}})
        return result


def last(database=podcast_coll):
    index = database.count()
    return index


def total_pages(database=podcast_coll, current_page=None):
    """Returns a dictionary containing the page navigation"""
    pages = last(database) // 10 + 1
    if not current_page or current_page > pages:
        current_page = pages

    plus_10 = current_page + 1
    minus_10 = current_page - 1
    nav = {
        'latest': None,
        'minus_10': minus_10,
        'plus_10': plus_10,
        'first': 1,
        'total': pages,
        'current': current_page
    }

    return nav


def podcast_page(page=None, database=podcast_coll):
    """returns podcast items for that page"""
    if not page:
        page = last()
    upper_limit = page * 10
    episodes = []
    coll = database.find({'episode_number': {'$lte': upper_limit}},
                         sort=[('episode_number', DES)], limit=10)
    for episode in coll:
        episodes.append(episode)
    return episodes
