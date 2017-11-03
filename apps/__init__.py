from flask import Flask

app = Flask(__name__)

app.config.from_object('config')

from apps.web_api.views import mod
from apps.frontend.views import mod
from apps.slack_api.views import mod
from apps.courses.views import mod
from mongo import auth
auth
