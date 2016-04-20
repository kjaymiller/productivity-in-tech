"""Rename File simply renames a file given in two ways
    1. All letters are lowered
    2. spaces are replaced with underscores"""

import re


def get_filename(path):
    """ returns the last part of the path which would be the filename"""
    filename = path.split('/')[-1]
    return filename
