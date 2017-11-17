from flask_testing import TestCase
import pytest
from flask import url_for

class MyTest(TestCase):

	def create_app(self):

		app = Flask(__name__)
		app.config['TESTING'] = True
		return app

@pytest.fixture
def app():
	app = create_app()
	return app