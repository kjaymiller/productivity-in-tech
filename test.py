from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

    # Validate All Pages Are Reachable    
    def test_index_slash(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='text/html')
        self.assertEqual(response.status_code, 200)

    def test_index_slashindex(self):
        tester = app.test_client(self)
        response = tester.get('/index', content_type='text/html')
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='text/html')
        self.assertEqual(response.status_code, 200)
if __name__ == '__main__':
    unittest.main()
