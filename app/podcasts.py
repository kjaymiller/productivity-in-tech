import re 


def ep_num_file(title):
    """ Retrieves the ep number from the import filename"""
    result = re.search(r'(ep){0,1} {0,1}(?P<ep_num>[0-9]+)', title, re.I)
    return int(result.group('ep_num'))

