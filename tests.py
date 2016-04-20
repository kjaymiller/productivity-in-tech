# testing tools
from selenium import webdriver
from random import randint
from pymongo import MongoClient
from requests import get
import unittest

# tested modules
from app.podcasts import next_episode_number
from app.mongo import get_ep_number
from tools import (rename_file)

client = MongoClient('localhost', 27017)
db = client.test
podcasts = db.podcasts


def setup_db():
    num_entries = randint(1, 25)
    entries = [{'ep_num': entry} for entry in range(num_entries)]
    podcasts.insert_many(entries)
    return podcasts

    podcasts.drop


class TestSitePages(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS('phantomjs/bin/phantomjs')

    def test_Homepage(self):
        self.assertEqual(200, get('http://localhost:5000').status_code)

    def tearDown(self):
        self.driver.quit()


class TestTools(unittest.TestCase):
        def test_get_filename(self):
            self.assertEqual('bar.png', rename_file.get_filename('foo/bar.png'))

        def test_get_ep_number_not_included(self):
            filename = 'this_file.mp3'
            self.assertIsNone(get_ep_number(filename))

        def test_et_ep_number_included(self):
            ep_num = str(randint(1, 2000))
            filename = 'ep{}_this_file.mp3'.format(ep_num)
            self.assertEqual(ep_num, get_ep_number(filename))


class TestEpisodes(unittest.TestCase):
    @classmethod
    def SetUpClass(cls):
        setup_db()

    @classmethod
    def TearDownClass(cls):
        podcasts.drop()

    def test_finds_next_available_number(self):
        self.assertEqual(next_episode_number(podcasts),
                         podcasts.count() + 1)


if __name__ == '__main__':
    unittest.main()
