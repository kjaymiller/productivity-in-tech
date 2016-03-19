from app import app
from app import site_config

from flask import render_template, url_for


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', config=site_config)
