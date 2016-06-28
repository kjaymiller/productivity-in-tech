""" This program adds the content to the mongo database to the sketchnotes"""

from sys import argv
from pymongo import ReturnDocument
from mongo import podcast_coll as coll
from podcasts import ep_num_file


def discover_podcast_by_title(filename, filetext):
    """ figure out which episode you are referencing
accept the content based on the title of the file or the prompt.
1. Find the episode number
2. Update the "shownotes field in the database

TIPS: A hack you can use to quickly update is name the file the episode number.
"""

    ep_num = ep_num_file(filename)
    qry = coll.find_one_and_update({'episode_number': ep_num},
                                   {'$set': {'shownotes': filetext}},
                                  return_document=ReturnDocument.AFTER)


def main():
    with open(argv[1], 'r') as f:
        file_text = f.read()
        discover_podcast_by_title(argv[1], file_text)

if __name__ == '__main__':
    main()
