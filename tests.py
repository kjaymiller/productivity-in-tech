import unittest
from random import randint
from pymongo import MongoClient
from app.podcasts import next_episode_number


client = MongoClient('localhost', 27017)
db = client.test
podcasts = db.podcasts


def setup_db():
    num_entries = randint(1, 25)
    entries = [{'ep_num': entry} for entry in range(num_entries)]
    podcasts.insert_many(entries)
    return podcasts

    podcasts.drop


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
