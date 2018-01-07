from flask import Flask
from flask_mail import Mail

# LOAD APPLICATION AND FLASK TEMPLATE CONFIG DATA
app = Flask(__name__)
app.config.from_object('config')

#LOAD MAIL MODULE
mail = Mail(app)


#LOAD VIEWS AND BLUEPRINTS
from blueprints.base_site.views import site
from blueprints.users.views import users

# REGISTER OUR BLUEPRINT
app.register_blueprint(site)
app.register_blueprint(users, url_prefix='/users')
