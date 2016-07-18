from app import app
from pymongo import DESCENDING as DES
from app.mongo import podcast_coll
from app import site_config
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup)
from markdown import markdown


@app.route('/')
@app.route('/index')
def index():
    feature = podcast_coll.find_one(sort=[('episode_number', DES)])
    return render_template('index.html',
                           config=site_config,
                           feature=feature)


@app.route('/podcast/<episode_number>')
def play(episode_number):
    episode = podcast_coll.find_one({'episode_number': int(episode_number)})

    if 'shownotes' in episode.keys():
        shownotes = Markup(markdown(episode['shownotes']))

    else:
        shownotes = ''

    last = podcast_coll.count()
    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           last=last)


@app.route('/podcast')
@app.route('/podcasts')
@app.route('/podcast/archive')
@app.route('/podcasts/archive')
def podcast_archive():
    episodes = [x for x in podcast_coll.find(sort=[('episode_number', DES)],
                                             limit=10)]

    return render_template('podcast_archive.html', episodes=episodes)


@app.route('/podcast/latest')
def play_latest():
    last = podcast_coll.count()
    return play(last)


@app.route('/friends')
def friends_of_show():
    return render_template('friends.html')


@app.route('/about')
def about():
    with open('app/static/md/about.md') as about_pit:
        content = Markup(markdown(about_pit.read()))

    return render_template('about.html', content=content)


#Redirect Pages
@app.route('/fb')
def facebook():
    return redirect('https://facebook.com/groups/productivityintech')


@app.route('/support')
def support():
    return redirect('https://patreon.com/productivityintech')


@app.route('/join')
def join():
    return redirect('http://eepurl.com/bUCywj')
