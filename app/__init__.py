from flask import Flask
from flask_mail import Mail

# LOAD APPLICATION AND FLASK TEMPLATE CONFIG DATA
app = Flask(__name__)
app.config.from_object('config')

#LOAD MAIL MODULE
mail = Mail(app)


#LOAD VIEWS AND BLUEPRINTS
from app import views
from blueprints.users.views import users

# REGISTER OUR BLUEPRINT
app.register_blueprint(users, url_prefix='/users')


# Authenticate DBs
from mongo import auth
auth

