from flask import Flask
from flask_mail import Mail

# LOAD APPLICATION AND FLASK TEMPLATE CONFIG DATA
app = Flask(__name__)
app.config.from_object('config')

#LOAD MAIL MODULE
mail = Mail(app)


#LOAD VIEWS AND BLUEPRINTS
from blueprints.base_site.views import site_mod
from blueprints.users.views import users_mod
from blueprints.podcast.views import podcast_mod

# REGISTER OUR BLUEPRINT
app.register_blueprint(site_mod)
app.register_blueprint(users_mod, url_prefix='/users')
app.register_blueprint(podcast_mod, url_prefix='/podcast')
