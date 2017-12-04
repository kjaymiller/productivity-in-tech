from app import app
import unittest



class TestPageLoads(unittest.TestCase):
    """Test If All Pages Result in status_code, 200 when the correct method is sent"""

    # HELPER FUNCTIONS
    def response_tests_get_only(self, path, content_type='text/html'):
        tester = app.test_client(self)
        response_get = tester.get(path, content_type='text/html')
        self.assertEqual(response_get.status_code, 200)
        
        response_post = tester.post(path, content_type='text/html')
        self.assertEqual(response_post.status_code, 405)
        
        response_put = tester.put(path, content_type='text/html')
        self.assertEqual(response_put.status_code, 405)
        
        response_delete = tester.delete(path, content_type='text/html')
        self.assertEqual(response_delete.status_code, 405)
        
    # TEST CASES
    def test_index_slash(self):
        self.response_tests_get_only('/')

    def test_index_slashindex(self):
        self.response_tests_get_only('/index')

    def test_podcast(self):
        self.response_tests_get_only('/podcast')

    def test_pit_podcast(self):
        self.response_tests_get_only('/pitpodcast')    

    def test_pitpodcast_latest(self):
        self.response_tests_get_only('/pitpodcast/latest')

    def test_pitpodcast_last(self):
        self.response_tests_get_only('/pitpodcast/last')
    
    @unittest.skip("Need to provide episode_number")
    def test_pitpodcast_episode_number(self):
        pass

    @unittest.skip("Need to provide id")
    def test_pitpodcast_id(self):
        pass

    def test_podcast_latest(self):
        self.response_tests_get_only('/podcast/latest')   

    def test_podcast_last(self):
        self.response_tests_get_only('/podcast/last')

    @unittest.skip("Need to provide episode_number")
    def test_podcast_episode_number(self):
        pass 

    @unittest.skip("Need to provide id")
    def test_podcast_id(self):
        pass

    def test_blog(self):
        self.response_tests_get_only('/blog')

    @unittest.skip("Need to provide id")
    def test_blog_post(self):
        pass

if __name__ == '__main__':
    unittest.main()
