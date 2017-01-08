from app import app
from bson.objectid import ObjectId
from pymongo import (DESCENDING as DES)
from app import site_config
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup,
                   make_response,
                   request,
                   jsonify)

from markdown import markdown
from models import (last,
                    total_pages,
                    podcast_page,
                    latest_episode,
                    latest_post)

from db_config import (collections, Blog, authors)
import arrow

def get_collection(collection_name):
    """Returns the correct collection from the db_config collections"""
    if collection_name in collections:
        collection = collections[collection_name].collection
        return collection
    else: return

def post_slack_data(attachments=[], response_type='in_channel'):
    """compiles the attachments and generates the json data for a slack post"""
    data = {'attachments':attachments, 'response_type': response_type}
    return jsonify(data)

@app.route('/podcasts')
@app.route('/subscribe')
def podcasts():
    return render_template('podcasts.html', header=True)

@app.route('/fots/<oid>')
def get_image(oid):
    friend = friends_coll.find_one({'_id': ObjectId(oid)})
    photo = friend['photo']
    response = make_response(photo)
    response.mimetype = 'image/png'
    return response

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')


@app.route('/')
@app.route('/index')
@app.route('/pros')
def index():
    return render_template('index.html')


@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
def play(podcast, episode_number=0):
    if podcast == 'podcast':
        podcast = 'pitpodcast'

    podcast = collections[podcast.lower()]
    collection = podcast.collection
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
                           last=last_episode,
                           podcast=podcast,
                           header=True,
                           )

@app.route('/<podcast>')
@app.route('/<podcast>/list/<int:page>')
def podcast_archive(podcast, page=0):
    podcast = collections[podcast.lower()]
    collection = podcast.collection
    nav = total_pages(page=page, collection=collection)
    episodes = podcast_page(page=page, collection=collection)
    return render_template('podcast_archive.html', nav=nav, podcast=podcast,
                            episodes=episodes, header=True)

@app.route('/blog')
def blog():
    blog=Blog.collection.find(sort=[('publish_date', DES)])
    return render_template('blog.html', blog=blog, header=True)

@app.route('/blog/<lookup>')
def post(lookup=None):
    friendly_lookup = Blog.collection.find_one({'friendly': lookup})
    id_lookup = Blog.collection.find_one({'_id':ObjectId(lookup)})
    if friendly_lookup:
        entry = friendly_lookup
    elif id_lookup:
        entry = id_lookup
    else:
        return render_template('blog.html', blog=Blog.collection.find())
    content = Markup(entry['content']) # content is stored in html
    publish_date = arrow.get(entry['publish_date']).format('MMM DD, YYYY')

    return render_template('post.html',
                            entry=entry,
                            content=content,
                            publish_date = publish_date,
                            tag_length = len(entry['tags']),
                            author = authors[entry['author']],
                            header=True)


@app.route('/friends')
def friends_of_show():
    friends = friends_coll.find()
    return render_template('friends.html', friends=friends, header=True)


@app.route('/community')
@app.route('/join')
def join():
    return render_template('join.html', header=True)


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/support')
def support():
    return render_template('support.html', header=True)


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


@app.route('/patreon')
def patreon():
    """Redirects to Patreon Page"""
    return redirect('https://patreon.com/productivityintech')


@app.route('/support1')
@app.route('/support-one')
@app.route('/support-1')
@app.route('/support%201')
@app.route('/support%20one')
@app.route('/paypal')
def support1():
    """Redirects to personal Paypal Page"""
    return redirect('http://bit.ly/pitsupport1')


@app.route('/subscribe/<podcast>/<channel>')
def show_player(podcast, channel):
    url = collections[podcast][channel]
    return redirect(url)


@app.route('/api/slack/latest', methods=['GET', 'POST'])
def get_latest_episode():
    if request.method == 'POST':
        data = request.form
        podcast_name = data.get('text')

        if podcast_name in collections:
            podcast = collections[podcast_name]
            collection = get_collection(podcast_name)
            episode_number = last(collection)
            episode = collection.find_one({'episode_number': episode_number})

            # build url for podcast link
            base_url = 'http://productivityintech.com/'
            url = base_url + '{}/{}'.format(podcast_name, episode_number)
            abbreviation = podcast.abbreviation

            #build title for podcast link
            title = episode['title']
            show_title = '{} {}: {}'.format(abbreviation, episode_number, title)

            #compile data and return it
            attachments=[{'title': show_title, 'title_link': url}]
            return post_slack_data(attachments)

    else: return 'I think you meant to POST not GET'

@app.route('/api/slack/itunes', methods=['GET', 'POST'])
def get_itunes_link():
    if request.method == 'POST':
        data = request.form
        podcast_name = data.get('text')

        if collections[podcast_name]:
            podcast =  collections[podcast_name]
            name = podcast.name
            itunes_link = podcast.links[0].url #iTunes is 0 in that array
            itunes_text = 'Click to View the iTunes link for {}'.format(name)
            attachments=[{'title': itunes_text, 'title_link': itunes_link}]
            return post_slack_data(attachments)
