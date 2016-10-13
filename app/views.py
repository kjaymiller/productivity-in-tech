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
from app.podcasts import (last,
                          total_pages,
                          podcast_page)
from app.db_config import collections


@app.route('/fots/<oid>')
def get_image(oid):
    friend = collections['friends']['collection'].find_one({'_id': ObjectId(oid)})
    photo = friend['photo']
    response = make_response(photo)
    response.mimetype = 'image/png'
    return response


@app.route('/')
@app.route('/index')
def index():
    podcast = collections['pitpodcast']['collection'].find_one(sort=[('episode_number', DES)], limit=1)
    friends = collections['friends']['collection'].find()
    return render_template('index.html',
                           config=site_config,
                           podcast=podcast,
                           friends=friends)


@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
def play(podcast, episode_number=0):
    podcast = podcast.lower()
    collection = collections[podcast]['collection']
    last_episode = last(collection)

    if episode_number > last_episode or not episode_number:
        episode_number = last_episode

    episode = collection.find_one({'episode_number': episode_number})

    if 'description' in episode.keys():
        shownotes = Markup(markdown(episode['description']))
    else:
        shownotes = "I'm sorry but shownotes have not been completed for this episode"

    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           last=last(collections['pitpodcast']['collection']),
                           podcast=podcast,
                           )


@app.route('/<podcast>')
@app.route('/<podcast>/list/<int:page>')
def podcast_archive(podcast, page=0):
    podcast = podcast.lower()
    collection = collections[podcast]['collection']
    nav = total_pages(page=page, collection=collection)
    episodes = podcast_page(page=page, collection=collection)
    return render_template('podcast_archive.html', nav=nav, podcast=collections[podcast], episodes=episodes)

@app.route('/friends')
def friends_of_show():
    friends = collections['friends']['collection'].find()
    return render_template('friends.html', friends=friends)


# Rendered Templates
@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/counseling')
def counseling_schedule():
    return render_template('counseling-schedule.html')


@app.route('/subscribe')
def suscribe():
    return render_template('subscribe.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


# Redirect Pages
@app.route('/fb')
@app.route('/FB')
@app.route('/facebook')
@app.route('/Facebook')
def facebook():
    return redirect('https://facebook.com/groups/productivityintech')


@app.route('/twitter')
@app.route('/Twitter')
def twitter():
    return redirect('https://twitter.com/Prodintech')


@app.route('/support')
def support():
    """Redirects to Patreon Page"""
    return redirect('https://patreon.com/productivityintech')


@app.route('/support1')
@app.route('/support-one')
@app.route('/support-1')
@app.route('/support%201')
@app.route('/support%20one')
def support1():
    """Redirects to personal Paypal Page"""
    return redirect('http://bit.ly/pitsupport1')


@app.route('/blog')
def blog():
    """Blog redirects for the time being"""
    return redirect('https://medium.com/PITBlog')


@app.route('/<podcast>/<link>')
def itunes(podcast, link):
    if podcast == 'pitreflections':
        podcast = pitreflections

    else:
        podcast = pitpodcast

    if link.lower() in podcast:
         link = link.lower()

    else:
        link = 'itunes'

    return redirect(podcast[link])


@app.route('/google')
def android():
    return redirect('https://play.google.com/music/listen#/ps/Isoopwbe6zdbev5ijenegkcpp44')


@app.route('/tunein')
def tunein():
    return redirect('http://tunein.com/radio/Productivity-in-Tech-Podcast-p894677/')


@app.route('/stitcher')
def stitcher():
    return redirect('http://app.stitcher.com/browse/feed/85598/details')
