from app import app
from app.mongo import get_episode
from app import site_config

from feedparser import parse
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    feed = parse('https://productivityintech.libsyn.com/rss').entries[0]
    latest_episode = {
                    'title': feed.title

    }
    return render_template('base.html',
                           config=site_config,
                           episode=latest_episode)


@app.route('/play/<ep_number>')
def play(ep_number):
    audio = get_episode(int(ep_number))
    return render_template('play.html', audio=audio)
