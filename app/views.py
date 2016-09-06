from app import app
from bson.objectid import ObjectId
from pymongo import (DESCENDING as DES)
from app import site_config
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup,
                   make_response)
from markdown import markdown
from app.mongo import podcast_coll, extended_coll, friends_coll
from app.podcasts import (last,
                          total_pages,
                          podcast_page)


@app.route('/fots/<oid>')
def get_image(oid):
    friend = friends_coll.find_one({'_id': ObjectId(oid)})
    photo = friend['photo']
    response = make_response(photo)
    response.mimetype = 'image/png'
    return response

@app.route('/')
@app.route('/index')
def index():
    podcast = podcast_coll.find_one(sort=[('episode_number', DES)], limit=1)
    friends = friends_coll.find()
    return render_template('index.html',
                           config=site_config,
                           podcast=podcast,
                           friends=friends)


@app.route('/podcast/latest')
@app.route('/podcast/last')
@app.route('/podcast/<int:episode_number>')
def play(episode_number=last()):
    episode = podcast_coll.find_one({'episode_number': episode_number})

    if 'shownotes' in episode.keys():
        shownotes = Markup(markdown(episode['shownotes']))

    else:
        shownotes = ''

    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           last=last())


@app.route('/podcast')
@app.route('/podcasts')
@app.route('/podcasts/all')
@app.route('/podcasts/list')
@app.route('/podcast/list')
@app.route('/podcast/archive')
@app.route('/podcasts/archive')
@app.route('/podcast/list/<int:current_page>')
@app.route('/podcasts/list/page=<int:current_page>')
@app.route('/podcast/archive/page=<int:current_page>')
@app.route('/podcasts/archive/page=<int:current_page>')
def podcast_archive(current_page=0):
    nav = total_pages(current_page=current_page)
    episodes = podcast_page(page=current_page)
    return render_template('podcast_archive.html', nav=nav, episodes=episodes)


# Not Live Yet
""" @app.route('/friends')
def friends_of_show():
    return render_template('friends.html')

"""

# Redirect Pages
@app.route('/fb')
def facebook():
    return redirect('https://facebook.com/groups/productivityintech')


@app.route('/support')
def support():
    return redirect('https://patreon.com/productivityintech')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/blog')
def blog():
    return redirect('https://medium.com/PITBlog')
